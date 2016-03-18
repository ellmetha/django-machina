# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import shutil

from django.conf import settings
from django.core.urlresolvers import reverse
from faker import Factory as FakerFactory
from haystack.management.commands import clear_index
from haystack.management.commands import rebuild_index
from haystack.query import SearchQuerySet
import pytest

from machina.core.db.models import get_model
from machina.core.loading import get_class
from machina.test.factories import create_category_forum
from machina.test.factories import create_forum
from machina.test.factories import create_topic
from machina.test.factories import PostFactory
from machina.test.testcases import BaseClientTestCase

faker = FakerFactory.create()

Post = get_model('forum_conversation', 'Post')
Topic = get_model('forum_conversation', 'Topic')

PermissionHandler = get_class('forum_permission.handler', 'PermissionHandler')
assign_perm = get_class('forum_permission.shortcuts', 'assign_perm')


class TestFacetedSearchView(BaseClientTestCase):
    @pytest.yield_fixture(autouse=True)
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

        rebuild_index.Command().handle(interactive=False, verbosity=-1)

        yield

        # teardown
        # --

        clear_index.Command().handle(interactive=False, verbosity=-1)

    @classmethod
    def teardown_class(cls):
        shutil.rmtree(settings.HAYSTACK_CONNECTIONS['default']['PATH'])

    def test_can_search_forum_posts(self):
        # Setup
        correct_url = reverse('forum_search:search')
        get_data = {'q': self.topic_1.subject}
        # Run
        response = self.client.get(correct_url, data=get_data)
        # Check
        assert response.status_code == 200
        assert len(response.context['page'].object_list) == 1
        assert response.context['page'].object_list[0].object == self.post_1
