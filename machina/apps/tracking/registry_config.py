# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

# Local application / specific library imports


class TrackingRegistryConfig(AppConfig):
    label = 'tracking'
    name = 'machina.apps.tracking'
    verbose_name = _('Forum tracking')

    def ready(self):  # pragma: no cover
        from . import receivers  # noqa
