"""
    Forum app config
    ================

    This module contains the application configuration class - available in the Django app registry.
    For more information on this file, see https://docs.djangoproject.com/en/dev/ref/applications/

"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ForumAppConfig(AppConfig):
    label = 'forum'
    name = 'machina.apps.forum'
    verbose_name = _('Machina: Forum')

    def ready(self):
        """ Executes whatever is necessary when the application is ready. """
        from . import receivers  # noqa: F401
