# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.core.urlresolvers import reverse
from faker import Factory as FakerFactory
from guardian.shortcuts import assign_perm

# Local application / specific library imports
from machina.core.loading import get_class
from machina.test.factories import create_forum
from machina.test.factories import create_topic
from machina.test.factories import ForumReadTrackFactory
from machina.test.factories import PostFactory
from machina.test.testcases import BaseClientTestCase

faker = FakerFactory.create()

PermissionHandler = get_class('permission.handler', 'PermissionHandler')


class TestMarkForumsReadView(BaseClientTestCase):
    def setUp(self):
        super(TestMarkForumsReadView, self).setUp()

        # Permission handler
        self.perm_handler = PermissionHandler()

        # Set up a top-level forum
        self.top_level_forum = create_forum()

        # Set up a topic and some posts
        self.topic = create_topic(forum=self.top_level_forum, poster=self.user)
        self.post = PostFactory.create(topic=self.topic, poster=self.user)

        # Mark the forum as read
        ForumReadTrackFactory.create(forum=self.top_level_forum, user=self.user)

        # Assign some permissions
        assign_perm('can_read_forum', self.user, self.top_level_forum)

    def test_browsing_works(self):
        # Setup
        correct_url_1 = reverse('tracking:mark-all-forums-read')
        correct_url_2 = reverse('tracking:mark-subforums-read', kwargs={'pk': self.top_level_forum.pk})
        # Run
        response_1 = self.client.get(correct_url_1, follow=True)
        response_2 = self.client.get(correct_url_2, follow=True)
        # Check
        self.assertIsOk(response_1)
        self.assertIsOk(response_2)
