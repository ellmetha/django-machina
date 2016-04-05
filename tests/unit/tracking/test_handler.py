# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth import get_user
from django.contrib.auth.models import AnonymousUser
from django.test.client import Client
from faker import Factory as FakerFactory
import pytest

from machina.core.db.models import get_model
from machina.core.loading import get_class
from machina.test.factories import create_category_forum
from machina.test.factories import create_forum
from machina.test.factories import create_link_forum
from machina.test.factories import create_topic
from machina.test.factories import GroupFactory
from machina.test.factories import ForumReadTrackFactory
from machina.test.factories import PostFactory
from machina.test.factories import TopicReadTrackFactory
from machina.test.factories import UserFactory

faker = FakerFactory.create()

Forum = get_model('forum', 'Forum')
ForumReadTrack = get_model('forum_tracking', 'ForumReadTrack')
TopicReadTrack = get_model('forum_tracking', 'TopicReadTrack')

assign_perm = get_class('forum_permission.shortcuts', 'assign_perm')
PermissionHandler = get_class('forum_permission.handler', 'PermissionHandler')
TrackingHandler = get_class('forum_tracking.handler', 'TrackingHandler')


@pytest.mark.django_db
class TestTrackingHandler(object):
    @pytest.fixture(autouse=True)
    def setup(self):
        self.u1 = UserFactory.create()
        self.u2 = UserFactory.create()
        self.g1 = GroupFactory.create()
        self.u1.groups.add(self.g1)
        self.u2.groups.add(self.g1)

        # Permission handler
        self.perm_handler = PermissionHandler()

        # Tracking handler
        self.tracks_handler = TrackingHandler()

        self.top_level_cat_1 = create_category_forum()
        self.top_level_cat_2 = create_category_forum()

        self.forum_1 = create_forum(parent=self.top_level_cat_1)
        self.forum_2 = create_forum(parent=self.top_level_cat_1)
        self.forum_2_child_1 = create_link_forum(parent=self.forum_2)
        self.forum_2_child_2 = create_forum(parent=self.forum_2)
        self.forum_3 = create_forum(parent=self.top_level_cat_1)

        self.forum_4 = create_forum(parent=self.top_level_cat_2)

        self.topic = create_topic(forum=self.forum_2, poster=self.u1)
        PostFactory.create(topic=self.topic, poster=self.u1)

        # Initially u2 read the previously created topic
        ForumReadTrackFactory.create(forum=self.forum_2, user=self.u2)

        # Assign some permissions
        assign_perm('can_read_forum', self.g1, self.top_level_cat_1)
        assign_perm('can_read_forum', self.g1, self.top_level_cat_2)
        assign_perm('can_read_forum', self.g1, self.forum_1)
        assign_perm('can_read_forum', self.g1, self.forum_2)
        assign_perm('can_read_forum', self.g1, self.forum_2_child_2)

    def test_says_that_all_forums_are_read_for_users_that_are_not_authenticated(self):
        # Setup
        u3 = get_user(Client())
        # Run
        unread_forums = self.tracks_handler.get_unread_forums(Forum.objects.all(), u3)
        # Check
        assert not len(unread_forums)

    def test_cannot_say_that_a_forum_is_unread_if_it_is_not_visible_by_the_user(self):
        # Setup
        new_topic = create_topic(forum=self.forum_3, poster=self.u1)
        PostFactory.create(topic=new_topic, poster=self.u1)
        # Run
        unread_forums = self.tracks_handler.get_unread_forums(Forum.objects.all(), self.u2)
        # Check
        assert self.forum_3 not in unread_forums

    def test_says_that_all_topics_are_read_for_users_that_are_not_authenticated(self):
        # Setup
        u3 = get_user(Client())
        # Run
        unread_topics = self.tracks_handler.get_unread_topics(self.forum_2.topics.all(), u3)
        # Check
        assert not len(unread_topics)

    def test_returns_an_empty_list_of_topics_if_the_forum_has_no_topics(self):
        # Run & check
        unread_topics = self.tracks_handler.get_unread_topics(self.forum_4.topics.all(), self.u2)
        assert not len(unread_topics)

    def test_says_that_a_topic_with_a_creation_date_greater_than_the_forum_mark_time_is_unread(self):  # noqa
        # Setup
        new_topic = create_topic(forum=self.forum_2, poster=self.u1)
        PostFactory.create(topic=new_topic, poster=self.u1)
        # Run
        unread_topics = self.tracks_handler.get_unread_topics(self.forum_2.topics.all(), self.u2)
        # Check
        assert unread_topics == [new_topic, ]

    def test_says_that_a_topic_with_a_last_post_date_greater_than_the_forum_mark_time_is_unread(self):  # noqa
        # Setup
        PostFactory.create(topic=self.topic, poster=self.u1)
        # Run
        unread_topics = self.tracks_handler.get_unread_topics(self.forum_2.topics.all(), self.u2)
        # Check
        assert unread_topics == [self.topic, ]

    def test_says_that_a_topic_with_a_last_post_date_greater_than_its_mark_time_is_unread(self):
        # Setup
        TopicReadTrackFactory.create(topic=self.topic, user=self.u2)
        PostFactory.create(topic=self.topic, poster=self.u1)
        # Run
        unread_topics = self.tracks_handler.get_unread_topics(self.forum_2.topics.all(), self.u2)
        # Check
        assert unread_topics == [self.topic, ]

    def test_says_that_a_topic_is_unread_if_the_related_forum_is_not_marked(self):
        # Setup
        new_topic = create_topic(forum=self.forum_3, poster=self.u1)
        PostFactory.create(topic=new_topic, poster=self.u1)
        # Run
        unread_topics = self.tracks_handler.get_unread_topics(self.forum_3.topics.all(), self.u2)
        # Check
        assert unread_topics == [new_topic, ]

    def test_cannot_say_that_a_topic_is_unread_if_it_has_been_marked(self):
        # Setup
        PostFactory.create(topic=self.topic, poster=self.u1)
        new_topic = create_topic(forum=self.forum_2, poster=self.u1)
        TopicReadTrackFactory.create(topic=self.topic, user=self.u2)
        # Run
        unread_topics = self.tracks_handler.get_unread_topics(self.forum_2.topics.all(), self.u2)
        # Check
        assert unread_topics == [new_topic, ]

    def test_cannot_say_that_a_topic_is_unread_if_it_has_been_edited(self):
        # Setup
        TopicReadTrackFactory.create(topic=self.topic, user=self.u2)
        post = self.topic.posts.all()[0]
        post.content = faker.text()
        post.save()
        # Run
        unread_forums = self.tracks_handler.get_unread_forums(Forum.objects.all(), self.u2)
        unread_topics = self.tracks_handler.get_unread_topics(self.forum_2.topics.all(), self.u2)
        # Check
        assert not len(unread_forums)
        assert not len(unread_topics)

    def test_cannot_say_that_a_forum_is_unread_if_it_has_been_updated_without_new_topics_or_posts(self):  # noqa
        # Setup
        self.forum_2.save()
        # Run
        unread_forums = self.tracks_handler.get_unread_forums(Forum.objects.all(), self.u2)
        # Check
        assert not len(unread_forums)

    def test_can_mark_forums_read(self):
        # Setup
        new_topic = create_topic(forum=self.forum_2, poster=self.u1)
        PostFactory.create(topic=new_topic, poster=self.u1)
        # Run
        self.tracks_handler.mark_forums_read(Forum.objects.all(), self.u2)
        # Check
        assert list(self.tracks_handler.get_unread_forums(
            Forum.objects.all(), self.u2)) == []

    def test_marks_parent_forums_as_read_when_marking_a_list_of_forums_as_read(self):
        # Setup
        new_topic = create_topic(forum=self.forum_2_child_2, poster=self.u1)
        PostFactory.create(topic=new_topic, poster=self.u1)
        # Run
        self.tracks_handler.mark_forums_read([self.forum_2_child_2, ], self.u2)
        # Check
        assert list(self.tracks_handler.get_unread_forums(
            Forum.objects.all(), self.u2)) == []
        assert ForumReadTrack.objects.filter(user=self.u2).count() == 3

    def test_cannot_mark_parent_forums_as_read_when_marking_a_list_of_forums_as_read_if_they_have_unread_topics(self):  # noqa
        # Setup
        new_topic_1 = create_topic(forum=self.forum_2_child_2, poster=self.u1)
        new_topic_2 = create_topic(forum=self.forum_2, poster=self.u1)
        PostFactory.create(topic=new_topic_1, poster=self.u1)
        PostFactory.create(topic=new_topic_2, poster=self.u1)
        # Run
        self.tracks_handler.mark_forums_read([self.forum_2_child_2, ], self.u2)
        # Check
        assert set(self.tracks_handler.get_unread_forums(
            Forum.objects.all(), self.u2)) == set([self.top_level_cat_1, self.forum_2, ])
        assert ForumReadTrack.objects.filter(user=self.u2).count() == 2

    def test_cannot_mark_forums_read_for_anonymous_users(self):
        # Setup
        new_topic = create_topic(forum=self.forum_2, poster=self.u1)
        PostFactory.create(topic=new_topic, poster=self.u1)
        initial_read_tracks_count = ForumReadTrack.objects.count()
        # Run
        self.tracks_handler.mark_forums_read(Forum.objects.all(), AnonymousUser())
        # Check
        assert ForumReadTrack.objects.count() == initial_read_tracks_count

    def test_can_mark_topics_read(self):
        # Setup
        new_topic = create_topic(forum=self.forum_2, poster=self.u1)
        PostFactory.create(topic=new_topic, poster=self.u1)
        # Run
        self.tracks_handler.mark_topic_read(new_topic, self.u2)
        # Check
        assert list(self.tracks_handler.get_unread_forums(
            [new_topic.forum, ], self.u2)) == []

    def test_marks_parent_forums_as_read_when_marking_a_topic_as_read(self):
        # Setup
        new_topic = create_topic(forum=self.forum_2_child_2, poster=self.u1)
        PostFactory.create(topic=new_topic, poster=self.u1)
        # Run
        self.tracks_handler.mark_topic_read(new_topic, self.u2)
        # Check
        assert list(self.tracks_handler.get_unread_forums(
            [self.forum_2_child_2, self.forum_2, self.top_level_cat_1, ], self.u2)) == []
        assert ForumReadTrack.objects.filter(user=self.u2).count() == 3
        assert not TopicReadTrack.objects.filter(user=self.u2).exists()

    def test_cannot_mark_topics_read_for_anonymous_users(self):
        # Setup
        new_topic = create_topic(forum=self.forum_2, poster=self.u1)
        PostFactory.create(topic=new_topic, poster=self.u1)
        initial_forum_read_tracks_count = ForumReadTrack.objects.count()
        initial_topics_read_tracks_count = TopicReadTrack.objects.count()
        # Run
        self.tracks_handler.mark_topic_read(new_topic, AnonymousUser())
        # Check
        assert ForumReadTrack.objects.count() == initial_forum_read_tracks_count
        assert TopicReadTrack.objects.count() == initial_topics_read_tracks_count
