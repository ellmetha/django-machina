# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.conf.urls import patterns
from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

# Local application / specific library imports
from machina.core.app import Application
from machina.core.loading import get_class


class ModerationApp(Application):
    name = 'forum-moderation'

    def get_urls(self):
        urls = [
        ]
        return patterns('', *urls)


application = ModerationApp()
