# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.conf.urls import patterns
from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

# Local application / specific library imports
from machina.core.app import Application
from machina.core.loading import get_class


class FeedsApp(Application):
    name = 'forum'

    latest_topics_feed = get_class('feeds.feeds', 'LastTopicsFeed')

    def get_urls(self):
        urls = [
            url(_(r'^topics/$'), self.latest_topics_feed(), name='latest-topics'),
            url(_(r'^forum/(?P<forum_pk>\d+)/topics/$'), self.latest_topics_feed(), name='forum-latest-topics'),
            url(_(r'^forum/(?P<forum_pk>\d+)/topics/all/$'), self.latest_topics_feed(), {'descendants': True}, name='forum-latest-topics-with-descendants'),
        ]
        return patterns('', *urls)


application = FeedsApp()
