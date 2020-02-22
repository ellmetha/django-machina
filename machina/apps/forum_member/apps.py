"""
    Forum member app config
    =======================

    This module contains the application configuration class - available in the Django app registry.
    For more information on this file, see https://docs.djangoproject.com/en/dev/ref/applications/

"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ForumMemberAppConfig(AppConfig):
    label = 'forum_member'
    name = 'machina.apps.forum_member'
    verbose_name = _('Machina: Forum members')

    def ready(self):
        """ Executes whatever is necessary when the application is ready. """
        from . import receivers  # noqa: F401
