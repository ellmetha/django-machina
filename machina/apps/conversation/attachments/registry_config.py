# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

# Local application / specific library imports


class AttachmentsRegistryConfig(AppConfig):
    label = 'attachments'
    name = 'machina.apps.conversation.attachments'
    verbose_name = _('Forum attachments')
