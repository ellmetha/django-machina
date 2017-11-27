# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from collections import Iterable

from django.conf import settings
from django.contrib.auth.decorators import REDIRECT_FIELD_NAME
from django.core.exceptions import ImproperlyConfigured
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import resolve_url
from django.utils.http import urlquote
from django.utils.six import string_types


class PermissionRequiredMixin(object):
    """
    This view mixin verifies if the current user has the permissions specified by the
    'permission_required' attribute. This 'permissions check' behavior can be updated
    in the 'perform_permissions_check()' method.

    It provides the following workflow:

        The mixin try to see if the view and the current user passes the permission check.

        If the permission check fails and if the user isn't logged in, redirect to
        settings.LOGIN_URL passing the current absolute path in the qyery string. Example:
        /accounts/login/?next=/forum/3/

        If the permission check fails and if the user is logged in, return a 403 error
        page.

    The permissions will be tested against a specific instance provided either by a
    `get_object()` method or by an `object` attribute. In the case where the permissions
    should be checked against an instance that is not the one associated with a specific
    DetailView, it is possible to write a `get_controlled_object` method to which it will
    be given priority over the methods and attributes mentioned previously.
    """
    login_url = settings.LOGIN_URL
    permission_required = None
    redirect_field_name = REDIRECT_FIELD_NAME

    def get_required_permissions(self, request):
        """
        Returns the required permissions to access the considered object.
        """
        perms = []

        if not self.permission_required:
            return perms

        if isinstance(self.permission_required, string_types):
            perms = [self.permission_required, ]
        elif isinstance(self.permission_required, Iterable):
            perms = [perm for perm in self.permission_required]
        else:
            raise ImproperlyConfigured(
                '\'PermissionRequiredMixin\' requires \'permission_required\' '
                'attribute to be set to \'<app_label>.<permission codename>\' but is set to {} '
                'instead'.format(self.permission_required)
            )
        return perms

    def perform_permissions_check(self, user, obj, perms):
        """
        Performs a permissions check in order to tell if the passed user
        can access the current view for the given object.
        By default, this method checks whether the given user has all the
        considered permissions in order to grant access. This behavior can
        be overridden in any subclass.
        """
        # Initializes a permission checker
        checker = self.request.forum_permission_handler._get_checker(user)
        # Check permissions
        return all(checker.has_perm(perm, obj) for perm in perms)

    def check_permissions(self, request):
        """
        Retrieve the controlled object and perform the permissions check.
        """
        obj = (hasattr(self, 'get_controlled_object') and self.get_controlled_object() or
               hasattr(self, 'get_object') and self.get_object() or getattr(self, 'object', None))
        user = request.user

        # Get the permissions to check
        perms = self.get_required_permissions(self)

        # Check permissions
        has_permissions = self.perform_permissions_check(user, obj, perms)

        if not has_permissions and not user.is_authenticated:
            return HttpResponseRedirect('{}?{}={}'.format(
                resolve_url(self.login_url),
                self.redirect_field_name,
                urlquote(request.get_full_path())
            ))
        elif not has_permissions:
            raise PermissionDenied

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        self.args = args
        self.kwargs = kwargs
        response = self.check_permissions(request)
        if response:
            return response
        return super(PermissionRequiredMixin, self).dispatch(request, *args, **kwargs)
