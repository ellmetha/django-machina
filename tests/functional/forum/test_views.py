# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.db.models import get_model
from guardian.shortcuts import assign_perm

# Local application / specific library imports
from machina.apps.forum.signals import forum_viewed
from machina.core.loading import get_class
from machina.test.factories import create_forum
from machina.test.factories import create_link_forum
from machina.test.testcases import BaseClientTestCase
from machina.test.utils import mock_signal_receiver

Post = get_model('conversation', 'Post')
Topic = get_model('conversation', 'Topic')

PermissionHandler = get_class('permission.handler', 'PermissionHandler')


class TestForumView(BaseClientTestCase):
    def setUp(self):
        super(TestForumView, self).setUp()

        # Permission handler
        self.perm_handler = PermissionHandler()

        # Set up a top-level forum and a link forum
        self.top_level_forum = create_forum()
        self.top_level_link = create_link_forum(link_redirects=True)

        # Assign some permissions
        assign_perm('can_read_forum', self.user, self.top_level_forum)
        assign_perm('can_read_forum', self.user, self.top_level_link)

    def test_browsing_works(self):
        # Setup
        correct_url = self.top_level_forum.get_absolute_url()
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        self.assertIsOk(response)

    def test_triggers_a_viewed_signal(self):
        # Setup
        forum_url, link_url = (self.top_level_forum.get_absolute_url(),
                               self.top_level_link.get_absolute_url())

        # Run & check
        for url in [forum_url, link_url]:
            with mock_signal_receiver(forum_viewed) as receiver:
                self.client.get(url, follow=True)
                self.assertEqual(receiver.call_count, 1)

    def test_redirects_to_the_link_of_a_link_forum(self):
        # Setup
        correct_url = self.top_level_link.get_absolute_url()
        # Run
        response = self.client.get(correct_url)
        # Check
        self.assertIsRedirect(response)
        self.assertEqual(response['Location'], self.top_level_link.link)

    def test_increases_the_redirects_counter_of_a_link_forum(self):
        # Setup
        correct_url = self.top_level_link.get_absolute_url()
        initial_redirects_count = self.top_level_link.link_redirects_count
        # Run
        self.client.get(correct_url)
        # Check
        top_level_link = self.top_level_link.__class__._default_manager.get(pk=self.top_level_link.pk)
        self.assertEqual(top_level_link.link_redirects_count, initial_redirects_count + 1)
