"""
    Forum moderation app config
    ===========================

    This module contains the application configuration class - available in the Django app registry.
    For more information on this file, see https://docs.djangoproject.com/en/dev/ref/applications/

"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ForumModerationAppConfig(AppConfig):
    label = 'forum_moderation'
    name = 'machina.apps.forum_moderation'
    verbose_name = _('Machina: Forum moderation')
