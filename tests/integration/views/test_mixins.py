# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from django.core.exceptions import PermissionDenied
from django.db.models import get_model
from django.test import RequestFactory
from django.test import TestCase
from django.views.generic import DetailView
from guardian.shortcuts import assign_perm

# Local application / specific library imports
from machina.core.loading import get_class
from machina.test.factories import create_forum
from machina.test.factories import UserFactory
from machina.views.mixins import PermissionRequiredMixin

Forum = get_model('forum', 'Forum')

PermissionHandler = get_class('permission.handler', 'PermissionHandler')


class TestPermissionRequiredMixin(TestCase):
    def setUp(self):
        self.user = UserFactory.create()
        self.factory = RequestFactory()

        # Permission handler
        self.perm_handler = PermissionHandler()

        # Set up a single forum
        self.forum = create_forum()

        # Assign some permissions
        assign_perm('can_see_forum', self.user, self.forum)

        self.mixin = PermissionRequiredMixin()

    def test_should_raise_if_the_permission_required_attribute_is_set_with_an_incorrect_value(self):
        # Setup
        self.mixin.object = self.forum
        self.mixin.permission_required = 10
        request = self.factory.get('/')
        request.user = self.user
        # Run & check
        with self.assertRaises(ImproperlyConfigured):
            self.mixin.check_permissions(request)

    def test_should_redirect_anonymous_users_to_login_url_if_access_is_not_granted(self):
        # Setup
        self.mixin.object = self.forum
        self.mixin.permission_required = 'can_read_forum'
        request = self.factory.get('/')
        request.user = AnonymousUser()
        # Run
        response = self.mixin.dispatch(request)
        # Check
        self.assertEqual(response.status_code, 302)  # Moved temporarily

    def test_should_return_http_response_forbiden_to_logged_in_users_if_access_is_not_granted(self):
        # Setup
        self.mixin.object = self.forum
        self.mixin.permission_required = ['can_read_forum', ]
        request = self.factory.get('/')
        request.user = self.user
        # Run & check
        with self.assertRaises(PermissionDenied):
            self.mixin.dispatch(request)

    def test_should_return_a_valid_response_if_access_is_granted(self):
        # Setup
        class ForumTestView(PermissionRequiredMixin, DetailView):
            permission_required = ['can_see_forum', ]

            def get_queryset(self):
                return Forum.objects.all()

        forum_view = ForumTestView()
        request = self.factory.get('/')
        request.user = self.user
        # Run
        response = forum_view.dispatch(request, pk=self.forum.pk)
        # Check
        self.assertEqual(response.status_code, 200)

    def test_should_consider_controlled_object_prior_to_builtin_objet_or_get_object_attributes(self):
        forum = self.forum

        # Setup
        class UserTestView(PermissionRequiredMixin, DetailView):
            permission_required = ['can_see_forum', ]

            def get_queryset(self):
                return User.objects.all()

            def get_controlled_object(self):
                return forum

        user_view = UserTestView()
        request = self.factory.get('/')
        request.user = self.user
        # Run
        response = user_view.dispatch(request, pk=self.user.pk)
        # Check
        self.assertEqual(response.status_code, 200)
