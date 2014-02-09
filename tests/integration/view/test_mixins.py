# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.core.exceptions import ImproperlyConfigured
from django.db.models import get_model
from django.test import RequestFactory
from django.test import TestCase

# Local application / specific library imports
from machina.test.factories import create_forum
from machina.test.factories import UserFactory
from machina.views.mixins import PermissionRequiredMixin

Forum = get_model('forum', 'Forum')


class TestPermissionRequiredMixin(TestCase):
    def setUp(self):
        self.user = UserFactory.create()
        self.factory = RequestFactory()

        # Set up a single forum
        self.forum = create_forum()

        self.mixin = PermissionRequiredMixin()

    def test_should_raise_if_the_permission_required_attribute_is_not_set(self):
        # Setup
        self.mixin.object = self.forum
        request = self.factory.get('/')
        request.user = self.user
        # Run
        with self.assertRaises(ImproperlyConfigured):
            self.mixin.check_permissions(request)
