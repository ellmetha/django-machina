# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import shutil

from django.conf import settings
from faker import Factory as FakerFactory
from haystack.management.commands import clear_index
from haystack.management.commands import rebuild_index
from haystack.query import SearchQuerySet
import pytest

from machina.apps.forum_search.forms import SearchForm
from machina.core.db.models import get_model
from machina.core.loading import get_class
from machina.test.factories import create_category_forum
from machina.test.factories import create_forum
from machina.test.factories import create_topic
from machina.test.factories import PostFactory
from machina.test.factories import UserFactory

faker = FakerFactory.create()

Post = get_model('forum_conversation', 'Post')
Topic = get_model('forum_conversation', 'Topic')

PermissionHandler = get_class('forum_permission.handler', 'PermissionHandler')
assign_perm = get_class('forum_permission.shortcuts', 'assign_perm')


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
        rebuild_index.Command().handle(interactive=False, verbosity=-1)
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
        rebuild_index.Command().handle(interactive=False, verbosity=-1)
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
        rebuild_index.Command().handle(interactive=False, verbosity=-1)
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
