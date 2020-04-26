"""
    Forum polls app config
    ======================

    This module contains the application configuration class - available in the Django app registry.
    For more information on this file, see https://docs.djangoproject.com/en/dev/ref/applications/

"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ForumPollsAppConfig(AppConfig):
    label = 'forum_polls'
    name = 'machina.apps.forum_conversation.forum_polls'
    verbose_name = _('Machina: Forum polls')
