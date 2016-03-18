# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ForumRegistryConfig(AppConfig):
    label = 'forum'
    name = 'machina.apps.forum'
    verbose_name = _('Machina: Forum')

    def ready(self):  # pragma: no cover
        from . import receivers  # noqa
