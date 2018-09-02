from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ModerationRegistryConfig(AppConfig):
    label = 'forum_moderation'
    name = 'machina.apps.forum_moderation'
    verbose_name = _('Machina: Forum moderation')
