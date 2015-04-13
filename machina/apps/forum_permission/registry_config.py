# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

# Local application / specific library imports


class PermissionRegistryConfig(AppConfig):
    label = 'forum_permission'
    name = 'machina.apps.forum_permission'
    verbose_name = _('Machina: Forum permissions')

    def ready(self):  # pragma: no cover
        from . import receivers  # noqa
