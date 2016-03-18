# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ConversationRegistryConfig(AppConfig):
    label = 'forum_conversation'
    name = 'machina.apps.forum_conversation'
    verbose_name = _('Machina: Forum conversations')

    def ready(self):  # pragma: no cover
        from . import receivers  # noqa
