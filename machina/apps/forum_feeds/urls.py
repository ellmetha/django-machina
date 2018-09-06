"""
    Forum feeds URLs
    ================

    This module defines URL patterns associated with the django-machina's ``forum_feeds``
    application.

"""

from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from machina.core.loading import get_class
from machina.core.urls import URLPatternsFactory


class ForumFeedsURLPatternsFactory(URLPatternsFactory):
    """ Allows to generate the URL patterns of the ``forum_feeds`` application. """

    app_namespace = 'forum_feeds'

    latest_topics_feed = get_class('forum_feeds.feeds', 'LastTopicsFeed')

    def get_urlpatterns(self):
        """ Returns the URL patterns managed by the considered factory / application. """
        return [
            url(_(r'^topics/$'), self.latest_topics_feed(), name='latest_topics'),
            url(
                _(r'^forum/(?P<forum_slug>[\w-]+)-(?P<forum_pk>\d+)/topics/$'),
                self.latest_topics_feed(),
                name='forum_latest_topics',
            ),
            url(
                _(r'^forum/(?P<forum_slug>[\w-]+)-(?P<forum_pk>\d+)/topics/all/$'),
                self.latest_topics_feed(),
                {'descendants': True},
                name='forum_latest_topics_with_descendants',
            ),
        ]


urlpatterns_factory = ForumFeedsURLPatternsFactory()
