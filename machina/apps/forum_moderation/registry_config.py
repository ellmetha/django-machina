# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

# Local application / specific library imports


class ModerationRegistryConfig(AppConfig):
    label = 'forum_moderation'
    name = 'machina.apps.forum_moderation'
    verbose_name = _('Machina: Forum moderation')
