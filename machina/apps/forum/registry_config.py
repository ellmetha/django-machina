# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

# Local application / specific library imports


class ForumRegistryConfig(AppConfig):
    label = 'forum'
    name = 'machina.apps.forum'
    verbose_name = _('Machina: Forum')

    def ready(self):  # pragma: no cover
        from . import receivers  # noqa
