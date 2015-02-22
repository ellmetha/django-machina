# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

# Local application / specific library imports


class SearchRegistryConfig(AppConfig):
    label = 'forum_search'
    name = 'machina.apps.forum_search'
    verbose_name = _('Machina: Forum searches')
