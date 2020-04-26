# import shutil

import pytest
# from django.conf import settings
# from django.core import management
from django.http import HttpRequest
# from django.test import override_settings
from faker import Faker

from machina.apps.forum_search.forms import PostgresSearchForm
from machina.core.db.models import get_model
from machina.core.loading import get_class
from machina.test.factories import (
    PostFactory, UserFactory, create_category_forum, create_forum, create_topic
)


faker = Faker()

Post = get_model('forum_conversation', 'Post')
Topic = get_model('forum_conversation', 'Topic')

PermissionHandler = get_class('forum_permission.handler', 'PermissionHandler')
assign_perm = get_class('forum_permission.shortcuts', 'assign_perm')


@pytest.mark.django_db
class TestPostgresSearchForm(object):
    @pytest.yield_fixture(autouse=True)
    def setup(self):
        # Permission handler
        self.perm_handler = PermissionHandler()

        # Create a basic user
        self.user = UserFactory.create(username='foobar')

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

        self.request = HttpRequest

        yield

    def test_can_search_forum_posts(self):
        # Setup
        self.request.user = self.user
        self.request.GET = {'q': self.topic_1.first_post.subject}
        form = PostgresSearchForm(self.request)
        # Run
        results = form.search()
        print(results)
        # Check
        assert form.is_valid()
        assert results[0].topic.forum.pk == self.topic_1.forum.pk

    def test_cannot_search_forum_posts_if_the_user_has_not_the_required_permissions(self):
        # Setup
        u1 = UserFactory.create()
        self.request.user = u1
        self.request.GET = {'q': self.topic_1.first_post.content}
        form = PostgresSearchForm(self.request)
        # Run
        results = form.search()
        # Check
        assert form.is_valid()
        assert results is None


'''
@pytest.mark.django_db
class TestSearchForm(object):
    @pytest.yield_fixture(autouse=True)
    def setup(self):
        # Permission handler
        self.perm_handler = PermissionHandler()

        # Create a basic user
        self.user = UserFactory.create(username='foobar')

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
        management.call_command('update_index', verbosity=0)

        yield

        # teardown
        # --

        management.call_command('clear_index', verbosity=0, interactive=False)

    @classmethod
    def teardown_class(cls):
        shutil.rmtree(settings.HAYSTACK_CONNECTIONS['default']['PATH'])

    def test_can_search_forum_posts(self):
        # Setup
        form = SearchForm(
            {'q': self.topic_1.first_post.subject},
            user=self.user,
        )
        # Run
        results = form.search()
        # Check
        assert form.is_valid()
        assert results[0].forum == self.topic_1.forum.pk

    def test_cannot_search_forum_posts_if_the_user_has_not_the_required_permissions(self):
        # Setup
        u1 = UserFactory.create()
        form = SearchForm(
            {'q': self.topic_1.first_post.content},
            user=u1,
        )
        # Run
        results = form.search()
        # Check
        assert form.is_valid()
        assert not len(results)

    def test_cannot_search_forum_posts_if_the_form_is_not_valid(self):
        # Setup
        form = SearchForm(
            {
                'q': self.topic_1.first_post.content,
                'search_forums': [1000, ],
            },
            user=self.user,
        )
        # Run
        results = form.search()
        # Check
        assert not len(results)

    def test_can_search_forum_posts_by_using_only_topic_subjects(self):
        # Setup
        form = SearchForm(
            {
                'q': self.topic_1.subject,
                'search_topics': True,

            },
            user=self.user,
        )
        # Run
        results = form.search()
        # Check
        assert form.is_valid()
        assert results[0].forum == self.topic_1.forum.pk

    def test_can_search_forum_posts_by_using_the_registered_poster_name(self):
        # Setup
        self.topic_1.first_post.subject = 'newsubject'
        self.topic_1.first_post.save()
        self.topic_2.first_post.subject = 'newsubject'
        self.topic_2.first_post.save()
        self.topic_3.first_post.subject = 'newsubject'
        self.topic_3.first_post.save()
        management.call_command('clear_index', verbosity=0, interactive=False)
        management.call_command('update_index', verbosity=0)
        form = SearchForm(
            {
                'q': 'newsubject',
                'search_poster_name': self.user.username,

            },
            user=self.user,
        )
        # Run
        results = form.search()
        # Check
        assert form.is_valid()
        assert [r.object for r in results] == [self.post_1, self.post_2, self.post_3, ]

    def test_can_search_forum_posts_by_using_the_anonymous_poster_name(self):
        # Setup
        self.topic_1.first_post.subject = 'newsubject'
        self.topic_1.first_post.save()
        self.topic_2.first_post.subject = 'newsubject'
        self.topic_2.first_post.save()
        self.topic_3.first_post.subject = 'newsubject'
        self.topic_3.first_post.save()
        post_4 = PostFactory.create(
            subject='newsubject', topic=self.topic_3, poster=None, username='newtest')
        management.call_command('clear_index', verbosity=0, interactive=False)
        management.call_command('update_index', verbosity=0)
        form = SearchForm(
            {
                'q': 'newsubject',
                'search_poster_name': 'newtest',

            },
            user=self.user,
        )
        # Run
        results = form.search()
        # Check
        assert form.is_valid()
        assert [r.object for r in results] == [post_4, ]

    def test_can_search_forum_posts_by_using_a_set_of_forums(self):
        # Setup
        self.topic_2.first_post.subject = self.topic_1.subject
        self.topic_2.first_post.save()
        management.call_command('clear_index', verbosity=0, interactive=False)
        management.call_command('update_index', verbosity=0)
        form = SearchForm(
            {
                'q': self.topic_1.subject,
                'search_forums': [self.forum_1.pk, self.forum_2.pk, ],

            },
            user=self.user,
        )
        # Run
        results = form.search()
        # Check
        assert form.is_valid()
        assert [r.object for r in results] == [self.post_1, self.post_2, ]


@pytest.mark.django_db
class TestPostgresSearchForm(object):
    @override_settings(MACHINA_SEARCH_ENGINE='postgres')
    @pytest.yield_fixture(autouse=True)
    def setup(self):
        management.call_command('migrate')
        # Permission handler
        self.perm_handler = PermissionHandler()

        # Create a basic user
        self.user = UserFactory.create(username='foobar')

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

        self.request = HttpRequest

        yield

    @override_settings(MACHINA_SEARCH_ENGINE='postgres')
    def test_can_search_forum_posts(self):
        # Setup
        self.request.user = self.user
        self.request.GET = {'q': self.topic_1.first_post.subject}
        form = PostgresSearchForm(request=self.request)
        # Run
        results = form.search()
        # Check
        assert form.is_valid()
        assert results[0].forum.pk == self.topic_1.forum.pk

    @override_settings(MACHINA_SEARCH_ENGINE='postgres')
    def test_cannot_search_forum_posts_if_the_user_has_not_the_required_permissions(self):
        # Setup
        u1 = UserFactory.create()
        self.request.user = u1
        self.request.GET = {'q': self.topic_1.first_post.content}
        form = PostgresSearchForm(request=self.request)
        # Run
        results = form.search()
        # Check
        assert form.is_valid()
        assert not len(results)

    @override_settings(MACHINA_SEARCH_ENGINE='postgres')
    def test_cannot_search_forum_posts_if_the_form_is_not_valid(self):
        # Setup
        self.request.user = self.user
        self.request.GET = {
            'q': self.topic_1.first_post.content,
            'search_forums': [1000, ],
        }
        form = PostgresSearchForm(request=self.request)
        # Run
        results = form.search()
        # Check
        assert not len(results)

    @override_settings(MACHINA_SEARCH_ENGINE='postgres')
    def test_can_search_forum_posts_by_using_only_topic_subjects(self):
        # Setup
        self.request.user = self.user
        self.request.GET = {
            'q': self.topic_1.subject,
            'search_topics': True,
        }
        form = PostgresSearchForm(request=self.request)
        # Run
        results = form.search()
        # Check
        assert form.is_valid()
        assert results[0].forum.pk == self.topic_1.forum.pk

    @override_settings(MACHINA_SEARCH_ENGINE='postgres')
    def test_can_search_forum_posts_by_using_the_registered_poster_name(self):
        # Setup
        self.topic_1.first_post.subject = 'newsubject'
        self.topic_1.first_post.save()
        self.topic_2.first_post.subject = 'newsubject'
        self.topic_2.first_post.save()
        self.topic_3.first_post.subject = 'newsubject'
        self.topic_3.first_post.save()

        self.request.user = self.user
        self.request.GET = {
            'q': 'newsubject',
            'search_poster_name': self.user.username,
        }
        form = PostgresSearchForm(request=self.request)
        # Run
        results = form.search()
        # Check
        assert form.is_valid()
        assert results == [self.post_1, self.post_2, self.post_3, ]

    @override_settings(MACHINA_SEARCH_ENGINE='postgres')
    def test_can_search_forum_posts_by_using_the_anonymous_poster_name(self):
        # Setup
        self.topic_1.first_post.subject = 'newsubject'
        self.topic_1.first_post.save()
        self.topic_2.first_post.subject = 'newsubject'
        self.topic_2.first_post.save()
        self.topic_3.first_post.subject = 'newsubject'
        self.topic_3.first_post.save()
        post_4 = PostFactory.create(
            subject='newsubject', topic=self.topic_3, poster=None, username='newtest')

        self.request.user = self.user
        self.request.GET = {
            'q': 'newsubject',
            'search_poster_name': 'newtest',
        }
        form = PostgresSearchForm(request=self.request)
        # Run
        results = form.search()
        # Check
        assert form.is_valid()
        assert results == [post_4, ]

    @override_settings(MACHINA_SEARCH_ENGINE='postgres')
    def test_can_search_forum_posts_by_using_a_set_of_forums(self):
        # Setup
        self.topic_2.first_post.subject = self.topic_1.subject
        self.topic_2.first_post.save()

        self.request.user = self.user
        self.request.GET = {
            'q': self.topic_1.subject,
            'search_forums': [self.forum_1.pk, self.forum_2.pk, ],
        }

        form = PostgresSearchForm(request=self.request)
        # Run
        results = form.search()
        # Check
        assert form.is_valid()
        assert results == [self.post_1, self.post_2, ]
'''
