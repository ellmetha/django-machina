# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.models import User
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.exceptions import ImproperlyConfigured
from django.core.exceptions import PermissionDenied
from django.test import RequestFactory
from django.views.generic import DetailView
import pytest

from machina.apps.forum_permission.middleware import ForumPermissionMiddleware
from machina.core.db.models import get_model
from machina.core.loading import get_class
from machina.test.factories import create_forum
from machina.test.factories import UserFactory

Forum = get_model('forum', 'Forum')

PermissionHandler = get_class('forum_permission.handler', 'PermissionHandler')
assign_perm = get_class('forum_permission.shortcuts', 'assign_perm')

PermissionRequiredMixin = get_class('forum_permission.viewmixins', 'PermissionRequiredMixin')


@pytest.mark.django_db
class TestPermissionRequiredMixin(object):
    @pytest.fixture(autouse=True)
    def setup(self):
        self.user = UserFactory.create()
        self.factory = RequestFactory()

        # Permission handler
        self.perm_handler = PermissionHandler()

        # Set up a single forum
        self.forum = create_forum()

        # Assign some permissions
        assign_perm('can_see_forum', self.user, self.forum)

        self.mixin = PermissionRequiredMixin()

    def get_request(self, url='/'):
        request = self.factory.get('/')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        return request

    def test_should_raise_if_the_permission_required_attribute_is_set_with_an_incorrect_value(self):
        # Setup
        self.mixin.object = self.forum
        self.mixin.permission_required = 10
        request = self.get_request()
        request.user = self.user
        ForumPermissionMiddleware().process_request(request)
        # Run & check
        with pytest.raises(ImproperlyConfigured):
            self.mixin.check_permissions(request)

    def test_should_redirect_anonymous_users_to_login_url_if_access_is_not_granted(self):
        # Setup
        self.mixin.object = self.forum
        self.mixin.permission_required = 'can_read_forum'
        request = self.get_request()
        request.user = AnonymousUser()
        ForumPermissionMiddleware().process_request(request)
        # Run
        response = self.mixin.dispatch(request)
        # Check
        assert response.status_code == 302  # Moved temporarily

    def test_should_return_http_response_forbiden_to_logged_in_users_if_access_is_not_granted(self):
        # Setup
        self.mixin.object = self.forum
        self.mixin.permission_required = ['can_read_forum', ]
        request = self.get_request()
        request.user = self.user
        ForumPermissionMiddleware().process_request(request)
        # Run & check
        with pytest.raises(PermissionDenied):
            self.mixin.dispatch(request)

    def test_should_return_a_valid_response_if_access_is_granted(self):
        # Setup
        class ForumTestView(PermissionRequiredMixin, DetailView):
            permission_required = ['can_see_forum', ]

            def get_queryset(self):
                return Forum.objects.all()

        forum_view = ForumTestView()
        request = self.get_request()
        request.user = self.user
        ForumPermissionMiddleware().process_request(request)
        # Run
        response = forum_view.dispatch(request, pk=self.forum.pk)
        # Check
        assert response.status_code == 200

    def test_should_consider_controlled_object_prior_to_builtin_objet_or_get_object_attributes(self):  # noqa
        forum = self.forum

        # Setup
        class UserTestView(PermissionRequiredMixin, DetailView):
            permission_required = ['can_see_forum', ]

            def get_queryset(self):
                return User.objects.all()

            def get_controlled_object(self):
                return forum

        user_view = UserTestView()
        request = self.get_request()
        request.user = self.user
        ForumPermissionMiddleware().process_request(request)
        # Run
        response = user_view.dispatch(request, pk=self.user.pk)
        # Check
        assert response.status_code == 200
