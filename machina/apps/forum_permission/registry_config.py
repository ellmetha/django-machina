# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class PermissionRegistryConfig(AppConfig):
    label = 'forum_permission'
    name = 'machina.apps.forum_permission'
    verbose_name = _('Machina: Forum permissions')

    def ready(self):  # pragma: no cover
        from . import receivers  # noqa
