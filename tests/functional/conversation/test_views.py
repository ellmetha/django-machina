# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.db.models import get_model
from guardian.shortcuts import assign_perm

# Local application / specific library imports
from machina.apps.conversation.signals import topic_viewed
from machina.core.loading import get_class
from machina.test.factories import create_forum
from machina.test.factories import create_topic
from machina.test.factories import PostFactory
from machina.test.testcases import BaseClientTestCase
from machina.test.utils import mock_signal_receiver

Post = get_model('conversation', 'Post')
Topic = get_model('conversation', 'Topic')

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
