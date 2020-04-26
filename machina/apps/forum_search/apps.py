"""
    Forum search app config
    =======================

    This module contains the application configuration class - available in the Django app registry.
    For more information on this file, see https://docs.djangoproject.com/en/dev/ref/applications/

"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ForumSearchAppConfig(AppConfig):
    label = 'forum_search'
    name = 'machina.apps.forum_search'
    verbose_name = _('Machina: Forum searches')
