"""
    Forum polls URLs
    ================

    This module defines URL patterns associated with the django-machina's ``forum_polls``
    application.

"""

from django.urls import path

from machina.core.loading import get_class
from machina.core.urls import URLPatternsFactory


class ForumPollsURLPatternsFactory(URLPatternsFactory):
    """ Allows to generate the URL patterns of the ``forum_polls`` application. """

    poll_vote_view = get_class('forum_conversation.forum_polls.views', 'TopicPollVoteView')

    def get_urlpatterns(self):
        """ Returns the URL patterns managed by the considered factory / application. """
        return [
            path('poll/<int:pk>/vote/', self.poll_vote_view.as_view(), name='topic_poll_vote'),
        ]


urlpatterns_factory = ForumPollsURLPatternsFactory()
