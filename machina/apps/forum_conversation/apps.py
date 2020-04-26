"""
    Forum conversation app config
    =============================

    This module contains the application configuration class - available in the Django app registry.
    For more information on this file, see https://docs.djangoproject.com/en/dev/ref/applications/

"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ForumConversationAppConfig(AppConfig):
    label = 'forum_conversation'
    name = 'machina.apps.forum_conversation'
    verbose_name = _('Machina: Forum conversations')

    def ready(self):
        """ Executes whatever is necessary when the application is ready. """
        from . import receivers  # noqa: F401
