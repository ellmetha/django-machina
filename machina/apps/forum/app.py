# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import unicode_literals

# Third party imports
from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

# Local application / specific library imports
from machina.core.app import Application
from machina.core.loading import get_class


class ForumApp(Application):
    name = 'forum'

    index_view = get_class('forum.views', 'IndexView')
    forum_view = get_class('forum.views', 'ForumView')

    def get_urls(self):
        return [
            url(r'^$', self.index_view.as_view(), name='index'),
            url(_(r'^forum/(?P<slug>[\w-]+)-(?P<pk>\d+)/$'), self.forum_view.as_view(), name='forum'),
        ]


application = ForumApp()
