from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class FeedsRegistryConfig(AppConfig):
    label = 'forum_feeds'
    name = 'machina.apps.forum_feeds'
    verbose_name = _('Machina: Forum feeds')
