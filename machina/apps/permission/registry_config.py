# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

# Local application / specific library imports


class PermissionRegistryConfig(AppConfig):
    label = 'permission'
    name = 'machina.apps.permission'
    verbose_name = _('Forum permissions')
