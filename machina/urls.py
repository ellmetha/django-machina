"""
    Machina URLs
    ============

    This module imports all the URLs defined by the forum-related applications.

"""

from django.urls import include, path
from django.utils.translation import ugettext_lazy as _

from machina.core.loading import get_class
from machina.core.urls import URLPatternsFactory


class BoardURLPatternsFactory(URLPatternsFactory):
    """ Allows to generate the URL patterns of the whole forum application. """

    forum_urlpatterns_factory = get_class('forum.urls', 'urlpatterns_factory')
    conversation_urlpatterns_factory = get_class('forum_conversation.urls', 'urlpatterns_factory')
    feeds_urlpatterns_factory = get_class('forum_feeds.urls', 'urlpatterns_factory')
    member_urlpatterns_factory = get_class('forum_member.urls', 'urlpatterns_factory')
    moderation_urlpatterns_factory = get_class('forum_moderation.urls', 'urlpatterns_factory')
    search_urlpatterns_factory = get_class('forum_search.urls', 'urlpatterns_factory')
    tracking_urlpatterns_factory = get_class('forum_tracking.urls', 'urlpatterns_factory')

    def get_urlpatterns(self):
        """ Returns the URL patterns managed by the considered factory / application. """
        return [
            path('', include(self.forum_urlpatterns_factory.urlpatterns)),
            path('', include(self.conversation_urlpatterns_factory.urlpatterns)),
            path(_('feeds/'), include(self.feeds_urlpatterns_factory.urlpatterns)),
            path(_('member/'), include(self.member_urlpatterns_factory.urlpatterns)),
            path(_('moderation/'), include(self.moderation_urlpatterns_factory.urlpatterns)),
            path(_('search/'), include(self.search_urlpatterns_factory.urlpatterns)),
            path(_('tracking/'), include(self.tracking_urlpatterns_factory.urlpatterns)),
        ]


urlpatterns_factory = BoardURLPatternsFactory()
urlpatterns = urlpatterns_factory.get_urlpatterns()
