# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class TrackingRegistryConfig(AppConfig):
    label = 'forum_tracking'
    name = 'machina.apps.forum_tracking'
    verbose_name = _('Machina: Forum tracking')

    def ready(self):  # pragma: no cover
        from . import receivers  # noqa
