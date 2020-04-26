"""
    Forum feeds app config
    ======================

    This module contains the application configuration class - available in the Django app registry.
    For more information on this file, see https://docs.djangoproject.com/en/dev/ref/applications/

"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ForumFeedsAppConfig(AppConfig):
    label = 'forum_feeds'
    name = 'machina.apps.forum_feeds'
    verbose_name = _('Machina: Forum feeds')
