# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.conf.urls import patterns
from django.conf.urls import url

# Local application / specific library imports
from machina.apps.forum.views import IndexView
from machina.core.app import Application


class ForumApp(Application):
    name = 'forum'

    index_view = IndexView

    def get_urls(self):
        urls = [
            url(r'^$', self.index_view.as_view(), name='index'),
        ]
        return patterns('', *urls)


application = ForumApp()
