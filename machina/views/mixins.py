# -*- coding: utf-8 -*-

# Standard library imports
from collections import Iterable

# Third party imports
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth.decorators import REDIRECT_FIELD_NAME
from django.http import HttpResponseForbidden
from django.http import HttpResponseRedirect
from django.utils.http import urlquote
from django.utils.six import string_types
from guardian.core import ObjectPermissionChecker

# Local application / specific library imports


class PermissionRequiredMixin(object):
    """
    This view mixin verifies if the current user has the permissions specified by the
    'permission_required' attribute.

    It provides the following workflow:

        The mixin try to see if the view and the current user passe the permission check.

        If the permission check fails and if the user isn't logged in, redirect to
        settings.LOGIN_URL passing the current absolute path in the qyery string. Example:
        /accounts/login/?next=/forum/3/

        If the permission check fails and if the user is logged in, return a 403 error
        page.

    The permissions will be tested against a specific instance provided either by a
    `get_object()` method or by an `object` attribute.
    """
    login_url = settings.LOGIN_URL
    permission_required = None
    redirect_field_name = REDIRECT_FIELD_NAME

    def get_required_permissions(self, request):
        if isinstance(self.permission_required, string_types):
            perms = [self.permission_required, ]
        elif isinstance(self.permission_required, Iterable):
            perms = [perm for perm in self.permission_required]
        else:
            raise ImproperlyConfigured(
                '\'PermissionRequiredMixin\' requires \'permission_required\' '
                'attribute to be set to \'<app_label>.<permission codename>\' but is set to {} instead'.format(
                    self.permission_required)
            )
        return perms

    def check_permissions(self, request):
        obj = (hasattr(self, 'get_object') and self.get_object()
               or getattr(self, 'object', None))
        user = request.user

        # Initializes a permission checker
        checker = ObjectPermissionChecker(user)

        # Get the permissions to check
        perms = self.get_required_permissions(self)

        # Check permissions
        has_permissions = all(checker.has_perm(perm, obj) for perm in perms)

        if not has_permissions and not user.is_authenticated():
            return HttpResponseRedirect("{}?{}={}".format(
                self.login_url,
                self.redirect_field_name,
                urlquote(request.get_full_path())
            ))
        elif not has_permissions:
            return HttpResponseForbidden()

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        self.args = args
        self.kwargs = kwargs
        response = self.check_permissions(request)
        if response:
            return response
        return super(PermissionRequiredMixin, self).dispatch(request, *args, **kwargs)
