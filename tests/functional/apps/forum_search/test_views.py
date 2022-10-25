import shutil

import pytest
from django.conf import settings
from django.core import management
from django.urls import reverse
from faker import Faker
from haystack.query import SearchQuerySet

from machina.core.db.models import get_model
from machina.core.loading import get_class
from machina.test.factories import PostFactory, create_category_forum, create_forum, create_topic
from machina.test.testcases import BaseClientTestCase


faker = Faker()

Post = get_model('forum_conversation', 'Post')
Topic = get_model('forum_conversation', 'Topic')

PermissionHandler = get_class('forum_permission.handler', 'PermissionHandler')
assign_perm = get_class('forum_permission.shortcuts', 'assign_perm')


class TestFacetedSearchView(BaseClientTestCase):
    @pytest.fixture(autouse=True)
    def setup(self):
        # Permission handler
        self.perm_handler = PermissionHandler()

        # Set up the following forum tree:
        #
        #     top_level_cat
        #         forum_1
        #         forum_2
        #             forum_2_child_1
        #     top_level_forum_1
        #     top_level_forum_2
        #         sub_cat
        #             sub_sub_forum
        #     top_level_forum_3
        #         forum_3
        #             forum_3_child_1
        #                 forum_3_child_1_1
        #                     deep_forum
        #     last_forum
        #
        self.top_level_cat = create_category_forum()

        self.forum_1 = create_forum(parent=self.top_level_cat)
        self.forum_2 = create_forum(parent=self.top_level_cat)
        self.forum_2_child_1 = create_forum(parent=self.forum_2)

        self.top_level_forum_1 = create_forum()

        self.top_level_forum_2 = create_forum()
        self.sub_cat = create_category_forum(parent=self.top_level_forum_2)
        self.sub_sub_forum = create_forum(parent=self.sub_cat)

        self.top_level_forum_3 = create_forum()
        self.forum_3 = create_forum(parent=self.top_level_forum_3)
        self.forum_3_child_1 = create_forum(parent=self.forum_3)
        self.forum_3_child_1_1 = create_forum(parent=self.forum_3_child_1)
        self.deep_forum = create_forum(parent=self.forum_3_child_1_1)

        self.last_forum = create_forum()

        # Set up a topic and some posts
        self.topic_1 = create_topic(forum=self.forum_1, poster=self.user)
        self.post_1 = PostFactory.create(topic=self.topic_1, poster=self.user)
        self.topic_2 = create_topic(forum=self.forum_2, poster=self.user)
        self.post_2 = PostFactory.create(topic=self.topic_2, poster=self.user)
        self.topic_3 = create_topic(forum=self.forum_2_child_1, poster=self.user)
        self.post_3 = PostFactory.create(topic=self.topic_3, poster=self.user)

        # Assign some permissions
        assign_perm('can_read_forum', self.user, self.top_level_cat)
        assign_perm('can_read_forum', self.user, self.forum_1)
        assign_perm('can_read_forum', self.user, self.forum_2)
        assign_perm('can_read_forum', self.user, self.forum_2_child_1)
        assign_perm('can_read_forum', self.user, self.top_level_forum_1)

        self.sqs = SearchQuerySet()

        management.call_command('clear_index', verbosity=0, interactive=False)

        yield

        # teardown
        # --

        management.call_command('clear_index', verbosity=0, interactive=False)

    @classmethod
    def teardown_class(cls):
        shutil.rmtree(settings.HAYSTACK_CONNECTIONS['default']['PATH'])

    def test_can_search_forum_posts(self):
        # Setup
        management.call_command('update_index', verbosity=0)
        correct_url = reverse('forum_search:search')
        get_data = {'q': self.topic_1.subject}
        # Run
        response = self.client.get(correct_url, data=get_data)
        # Check
        assert response.status_code == 200
        assert len(response.context['page'].object_list) == 1
        assert response.context['page'].object_list[0].object == self.post_1

    def test_can_search_with_pagination(self):
        """
        Check that pagination has well formed links
        """
        # Setup
        # Index 40 more posts in Elasticsearch (101 in total)
        PostFactory.create_batch(
            40,
            topic=self.topic_1,
            poster=self.user,
            content=self.post_1.content
        )

        management.call_command('rebuild_index', interactive=False)

        correct_url = reverse('forum_search:search')
        expected_string = str(self.post_1.content)
        get_data = {'q': expected_string}

        # Run
        response = self.client.get(correct_url, data=get_data)

        # Check
        content = response.content.decode()
        assert response.status_code == 200
        assert 'Your search has returned <b>41</b> results' in content
        # The post content is truncated in results
        assert content.count(f'{expected_string[:200]:s}...') == 20

        # 20 results per page and 2 panels of pagination (top and bottom)
        # check all li tags are well closed
        assert content.count(expected_string) == (3 + 1) * 2
        assert content.count('<li class="page-item">') == 3 * 2
        assert content.count('<li class="page-item active">') == 1 * 2
        assert content.count('<li class="page-item disabled">') == 1 * 2

        # check all links are well formed
        assert (
            '<li class="page-item active">'
            f'<a href="?q={expected_string:s}&amp;page=1" class="page-link">1</a>'
            '</li>'
        ) in content
        for page in range(2, 3):
            assert f'?q={expected_string:s}&amp;page={page}' in content
            assert (
                f'<li class="page-item"><a href="?q={expected_string:s}&amp;page={page}" '
                f'class="page-link">{page}</a></li>'
            ) in content
        assert 'page=4' not in content
