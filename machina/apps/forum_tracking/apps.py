"""
    Forum tracking app config
    =========================

    This module contains the application configuration class - available in the Django app registry.
    For more information on this file, see https://docs.djangoproject.com/en/dev/ref/applications/

"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ForumTrackingAppConfig(AppConfig):
    label = 'forum_tracking'
    name = 'machina.apps.forum_tracking'
    verbose_name = _('Machina: Forum tracking')

    def ready(self):
        """ Executes whatever is necessary when the application is ready. """
        from . import receivers  # noqa: F401
