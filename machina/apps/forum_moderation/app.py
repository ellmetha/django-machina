# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.conf.urls import patterns

# Local application / specific library imports
from machina.core.app import Application


class ModerationApp(Application):
    name = 'forum-moderation'

    def get_urls(self):
        urls = [
        ]
        return patterns('', *urls)


application = ModerationApp()
