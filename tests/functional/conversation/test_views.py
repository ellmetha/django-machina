# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.db.models import get_model
from guardian.shortcuts import assign_perm
from guardian.utils import get_anonymous_user

# Local application / specific library imports
from machina.apps.conversation.signals import topic_viewed
from machina.core.loading import get_class
from machina.test.factories import create_forum
from machina.test.factories import create_topic
from machina.test.factories import ForumReadTrackFactory
from machina.test.factories import PostFactory
from machina.test.factories import TopicReadTrackFactory
from machina.test.testcases import BaseClientTestCase
from machina.test.utils import mock_signal_receiver

ForumReadTrack = get_model('tracking', 'ForumReadTrack')
Post = get_model('conversation', 'Post')
Topic = get_model('conversation', 'Topic')
TopicReadTrack = get_model('tracking', 'TopicReadTrack')

PermissionHandler = get_class('permission.handler', 'PermissionHandler')


class TestTopicView(BaseClientTestCase):
    def setUp(self):
        super(TestTopicView, self).setUp()

        # Permission handler
        self.perm_handler = PermissionHandler()

        # Set up a top-level forum and a link forum
        self.top_level_forum = create_forum()

        # Set up a topic and some posts
        self.topic = create_topic(forum=self.top_level_forum, poster=self.user)
        self.post = PostFactory.create(topic=self.topic, poster=self.user)

        # Assign some permissions
        assign_perm('can_read_forum', self.user, self.top_level_forum)

    def test_browsing_works(self):
        # Setup
        correct_url = self.topic.get_absolute_url()
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        self.assertIsOk(response)

    def test_triggers_a_viewed_signal(self):
        # Setup
        correct_url = self.topic.get_absolute_url()
        # Run & check
        with mock_signal_receiver(topic_viewed) as receiver:
            self.client.get(correct_url, follow=True)
            self.assertEqual(receiver.call_count, 1)

    def test_increases_the_views_counter_of_the_topic(self):
        # Setup
        correct_url = self.topic.get_absolute_url()
        initial_views_count = self.topic.views_count
        # Run
        self.client.get(correct_url)
        # Check
        topic = self.topic.__class__._default_manager.get(pk=self.topic.pk)
        self.assertEqual(topic.views_count, initial_views_count + 1)

    def test_marks_the_related_forum_as_read_if_no_other_unread_topics_are_present(self):
        # Setup
        TopicReadTrackFactory.create(topic=self.topic, user=self.user)
        PostFactory.create(topic=self.topic, poster=self.user)
        correct_url = self.topic.get_absolute_url()
        # Run
        self.client.get(correct_url)
        # Check
        forum_tracks = ForumReadTrack.objects.all()
        self.assertEqual(forum_tracks.count(), 1)
        self.assertEqual(forum_tracks[0].forum, self.topic.forum)
        self.assertEqual(forum_tracks[0].user, self.user)

    def test_marks_the_related_topic_as_read_if_other_unread_topics_are_present(self):
        # Setup
        ForumReadTrackFactory.create(forum=self.top_level_forum, user=self.user)
        new_topic = create_topic(forum=self.top_level_forum, poster=self.user)
        PostFactory.create(topic=new_topic, poster=self.user)
        correct_url = self.topic.get_absolute_url()
        # Run
        self.client.get(correct_url)
        # Check
        topic_tracks = TopicReadTrack.objects.all()
        self.assertEqual(topic_tracks.count(), 1)
        self.assertEqual(topic_tracks[0].topic, self.topic)
        self.assertEqual(topic_tracks[0].user, self.user)

    def test_cannot_create_any_track_if_the_user_is_not_authenticated(self):
        # Setup
        assign_perm('can_read_forum', get_anonymous_user(), self.top_level_forum)
        self.client.logout()
        correct_url = self.topic.get_absolute_url()
        # Run
        self.client.get(correct_url)
        # Check
        forum_tracks = ForumReadTrack.objects.all()
        topic_tracks = TopicReadTrack.objects.all()
        self.assertFalse(len(forum_tracks))
        self.assertFalse(len(topic_tracks))
