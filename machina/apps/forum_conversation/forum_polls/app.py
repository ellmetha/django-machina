# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url

from machina.core.app import Application
from machina.core.loading import get_class


class PollsApp(Application):
    name = None

    poll_vote_view = get_class('forum_conversation.forum_polls.views', 'TopicPollVoteView')

    def get_urls(self):
        return [
            url(r'^poll/(?P<pk>\d+)/vote/$', self.poll_vote_view.as_view(), name='topic_poll_vote'),
        ]


application = PollsApp()
