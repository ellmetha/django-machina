# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.db.models import get_model
from guardian.shortcuts import assign_perm

# Local application / specific library imports
from machina.core.loading import get_class
from machina.test.factories import create_forum
from machina.test.testcases import BaseClientTestCase

Post = get_model('conversation', 'Post')
Topic = get_model('conversation', 'Topic')

PermissionHandler = get_class('permission.handler', 'PermissionHandler')


class TestForumView(BaseClientTestCase):
    def setUp(self):
        super(TestForumView, self).setUp()

        # Permission handler
        self.perm_handler = PermissionHandler()

        # Set up a top-level forum
        self.top_level_forum = create_forum()

        # Assign some permissions
        assign_perm('can_read_forum', self.user, self.top_level_forum)

    def test_browsing_works(self):
        # Setup
        correct_url = self.top_level_forum.get_absolute_url()
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        self.assertIsOk(response)
