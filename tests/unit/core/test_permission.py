# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.test import TestCase

# Local application / specific library imports
from machina.conf import settings as machina_settings
from machina.core.permission import ObjectPermissionChecker
from machina.test.factories import create_forum
from machina.test.factories import UserFactory


class TestObjectPermissionChecker(TestCase):
    def setUp(self):
        self.forum = create_forum()
        machina_settings.DEFAULT_AUTHENTICATED_USER_PERMISSIONS= {
            'forum.forum': ['can_see_forum', ],
        }

    def tearDown(self):
        machina_settings.DEFAULT_AUTHENTICATED_USER_PERMISSIONS= {}

    def test_allows_the_use_of_default_permissions(self):
        # Setup
        user = UserFactory.create()
        checker = ObjectPermissionChecker(user)
        # Run & check
        self.assertTrue(checker.has_perm('can_see_forum', self.forum))
