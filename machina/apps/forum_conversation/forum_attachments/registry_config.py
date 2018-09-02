from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class AttachmentsRegistryConfig(AppConfig):
    label = 'forum_attachments'
    name = 'machina.apps.forum_conversation.forum_attachments'
    verbose_name = _('Machina: Forum attachments')
