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

    topic_lock_view = get_class('forum_moderation.views', 'TopicLockView')
    topic_delete_view = get_class('forum_moderation.views', 'TopicDeleteView')
    topic_move_view = get_class('forum_moderation.views', 'TopicMoveView')

    def get_urls(self):
        urls = [
            url(_(r'^topic/(?P<slug>[\w-]+)-(?P<pk>\d+)/lock/$'), self.topic_lock_view.as_view(), name='topic-lock'),
            url(_(r'^topic/(?P<slug>[\w-]+)-(?P<pk>\d+)/delete/$'), self.topic_delete_view.as_view(), name='topic-delete'),
            url(_(r'^topic/(?P<slug>[\w-]+)-(?P<pk>\d+)/move/$'), self.topic_move_view.as_view(), name='topic-move'),
        ]
        return patterns('', *urls)


application = ModerationApp()
