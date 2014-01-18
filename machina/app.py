# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.conf.urls import include
from django.conf.urls import patterns
from django.conf.urls import url

# Local application / specific library imports
from machina.core.app import Application
from machina.core.loading import get_class


class BoardApp(Application):
    name = None

    forum_app = get_class('forum.app', 'application')

    def get_urls(self):
        urls = [
            url(r'', include(self.forum_app.urls)),
        ]
        return patterns('', *urls)


board = application = BoardApp()
