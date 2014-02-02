# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.conf.urls import patterns
from django.conf.urls import url

# Local application / specific library imports
from machina.apps.forum import views
from machina.core.app import Application


class ForumApp(Application):
    name = 'forum'

    index_view = views.IndexView
    forum_view = views.ForumView

    def get_urls(self):
        urls = [
            url(r'^$', self.index_view.as_view(), name='index'),
            url(r'^forum/(?P<pk>\d+)/$', self.forum_view.as_view(), name='forum'),
        ]
        return patterns('', *urls)


application = ForumApp()
