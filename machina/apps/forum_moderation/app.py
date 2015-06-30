# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import unicode_literals

# Third party imports
from django.conf.urls import patterns
from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

# Local application / specific library imports
from machina.core.app import Application
from machina.core.loading import get_class


class ModerationApp(Application):
    name = 'forum-moderation'

    topic_close_view = get_class('forum_moderation.views', 'TopicCloseView')

    def get_urls(self):
        urls = [
            url(_(r'^topic/(?P<slug>[\w-]+)-(?P<pk>\d+)/close/$'), self.topic_close_view.as_view(), name='topic-close'),
        ]
        return patterns('', *urls)


application = ModerationApp()
