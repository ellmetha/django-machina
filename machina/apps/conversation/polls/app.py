# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.conf.urls import patterns
from django.conf.urls import url

# Local application / specific library imports
from machina.apps.conversation.polls import views
from machina.core.app import Application


class PollsApp(Application):
    name = None

    poll_vote_view = views.TopicPollVoteView

    def get_urls(self):
        urls = [
            url(r'^poll/(?P<pk>\d+)/vote/$', self.poll_vote_view.as_view(), name='topic-poll-vote'),
        ]
        return patterns('', *urls)


application = PollsApp()
