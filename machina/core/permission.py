# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import unicode_literals

# Third party imports
from guardian.core import ObjectPermissionChecker as BaseObjectPermissionChecker
from machina.conf import settings as machina_settings

# Local application / specific library imports


class ObjectPermissionChecker(BaseObjectPermissionChecker):
    def get_perms(self, obj):
        """
        Overrides the ``get_perms`` method of django-guardian in order to
        support default permissions for authenticated users.
        """
        default_auth_perms = machina_settings.DEFAULT_AUTHENTICATED_USER_PERMISSIONS
        perms = super(ObjectPermissionChecker, self).get_perms(obj)

        if not perms and default_auth_perms \
                and self.user and self.user.is_authenticated():
            app = obj._meta.app_label
            model_name = getattr(obj._meta, 'model_name', None) or obj._meta.module_name
            app_model = '{0}.{1}'.format(app, model_name)

            if app_model in default_auth_perms and default_auth_perms[app_model]:
                perms.extend(default_auth_perms[app_model])

        return perms
