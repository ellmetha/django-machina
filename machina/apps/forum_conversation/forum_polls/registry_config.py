# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class PollsRegistryConfig(AppConfig):
    label = 'forum_polls'
    name = 'machina.apps.forum_conversation.forum_polls'
    verbose_name = _('Machina: Forum polls')
