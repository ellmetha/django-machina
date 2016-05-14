# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.test.client import RequestFactory
import pytest

from machina.apps.forum_feeds.feeds import LastTopicsFeed
from machina.core.db.models import get_model
from machina.core.loading import get_class
from machina.test.factories import create_category_forum
from machina.test.factories import create_forum
from machina.test.factories import create_topic
from machina.test.factories import PostFactory
from machina.test.factories import UserFactory

Post = get_model('forum_conversation', 'Post')
Topic = get_model('forum_conversation', 'Topic')

PermissionHandler = get_class('forum_permission.handler', 'PermissionHandler')
assign_perm = get_class('forum_permission.shortcuts', 'assign_perm')


@pytest.mark.django_db
class TestLastTopicsFeed(object):
    @pytest.fixture(autouse=True)
    def setup(self):
        self.factory = RequestFactory()
        self.user = UserFactory.create()

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

    def test_can_return_all_the_topics_that_can_be_read_by_the_current_user(self):
        # Setup
        feed = LastTopicsFeed()
        request = self.factory.get('/')
        request.user = self.user
        request.forum_permission_handler = PermissionHandler()
        # Run
        feed.get_object(request)
        topics = feed.items()
        # Check
        assert list(topics) == [self.topic_3, self.topic_2, self.topic_1, ]

    def test_can_return_all_the_topics_that_can_be_read_by_the_current_user_in_a_forum_without_its_descendants(self):  # noqa
        # Setup
        feed = LastTopicsFeed()
        request = self.factory.get('/')
        request.user = self.user
        request.forum_permission_handler = PermissionHandler()
        # Run
        feed.get_object(request, forum_pk=self.forum_2.pk, descendants=False)
        topics = feed.items()
        # Check
        assert list(topics) == [self.topic_2, ]

    def test_can_return_all_the_topics_that_can_be_read_by_the_current_user_in_a_forum_including_its_descendants(self):  # noqa
        # Setup
        feed = LastTopicsFeed()
        request = self.factory.get('/')
        request.user = self.user
        request.forum_permission_handler = PermissionHandler()
        # Run
        feed.get_object(request, forum_pk=self.forum_2.pk, descendants=True)
        topics = feed.items()
        # Check
        assert list(topics) == [self.topic_3, self.topic_2, ]

    def test_plucation_dates_correspond_to_the_topic_creation_dates(self):
        # Setup
        feed = LastTopicsFeed()
        request = self.factory.get('/')
        request.user = self.user
        request.forum_permission_handler = PermissionHandler()
        # Run & check
        assert feed.item_pubdate(self.topic_2) == self.topic_2.created

    def test_can_return_the_proper_item_link(self):
        # Setup
        feed = LastTopicsFeed()
        request = self.factory.get('/')
        request.user = self.user
        request.forum_permission_handler = PermissionHandler()
        # Run & check
        assert feed.item_link(self.topic_2) == reverse(
            'forum_conversation:topic', kwargs={
                'forum_slug': self.topic_2.forum.slug, 'forum_pk': self.topic_2.forum.pk,
                'slug': self.topic_2.slug, 'pk': self.topic_2.id,
            })
