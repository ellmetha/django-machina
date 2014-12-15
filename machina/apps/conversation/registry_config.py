# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

# Local application / specific library imports


class ConversationRegistryConfig(AppConfig):
    label = 'conversation'
    name = 'machina.apps.conversation'
    verbose_name = _('Forum conversations')

    def ready(self):
        from . import receivers  # noqa
