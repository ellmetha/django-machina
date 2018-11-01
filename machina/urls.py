"""
    Machina URLs
    ============

    This module imports all the URLs defined by the forum-related applications.

"""

from django.conf.urls import include, url
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
            url(r'', include(self.forum_urlpatterns_factory.urlpatterns)),
            url(r'', include(self.conversation_urlpatterns_factory.urlpatterns)),
            url(_(r'^feeds/'), include(self.feeds_urlpatterns_factory.urlpatterns)),
            url(_(r'^member/'), include(self.member_urlpatterns_factory.urlpatterns)),
            url(_(r'^moderation/'), include(self.moderation_urlpatterns_factory.urlpatterns)),
            url(_(r'^search/'), include(self.search_urlpatterns_factory.urlpatterns)),
            url(_(r'^tracking/'), include(self.tracking_urlpatterns_factory.urlpatterns)),
        ]


urlpatterns_factory = BoardURLPatternsFactory()
urlpatterns = urlpatterns_factory.get_urlpatterns()
