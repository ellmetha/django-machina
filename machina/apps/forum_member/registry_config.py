# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

# Local application / specific library imports


class MemberRegistryConfig(AppConfig):
    label = 'forum_member'
    name = 'machina.apps.forum_member'
    verbose_name = _('Machina: Forum members')

    def ready(self):  # pragma: no cover
        from . import receivers  # noqa
