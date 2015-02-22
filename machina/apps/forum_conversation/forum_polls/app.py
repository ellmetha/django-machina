# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.conf.urls import patterns
from django.conf.urls import url

# Local application / specific library imports
from machina.core.app import Application
from machina.core.loading import get_class


class PollsApp(Application):
    name = None

    poll_vote_view = get_class('forum_conversation.forum_polls.views', 'TopicPollVoteView')

    def get_urls(self):
        urls = [
            url(r'^poll/(?P<pk>\d+)/vote/$', self.poll_vote_view.as_view(), name='topic-poll-vote'),
        ]
        return patterns('', *urls)


application = PollsApp()
