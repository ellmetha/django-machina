# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.conf.urls import patterns
from django.conf.urls import url

# Local application / specific library imports
from machina.apps.tracking import views
from machina.core.app import Application


class TrackingApp(Application):
    name = 'tracking'

    mark_forums_read_view = views.MarkForumsReadView

    def get_urls(self):
        urls = [
            url(r'^mark/forums/$', self.mark_forums_read_view.as_view(), name='mark-all-forums-read'),
            url(r'^mark/forums/(?P<pk>\d+)/$', self.mark_forums_read_view.as_view(), name='mark-subforums-read'),
        ]
        return patterns('', *urls)


application = TrackingApp()
