from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class SearchRegistryConfig(AppConfig):
    label = 'forum_search'
    name = 'machina.apps.forum_search'
    verbose_name = _('Machina: Forum searches')
