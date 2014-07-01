# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.conf.urls import patterns
from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

# Local application / specific library imports
from machina.apps.feeds import feeds
from machina.core.app import Application


class FeedsApp(Application):
    name = 'forum'

    latest_topics_feed = feeds.LastTopicsFeed

    def get_urls(self):
        urls = [
            url(_(r'^topics/$'), self.latest_topics_feed()),
        ]
        return patterns('', *urls)


application = FeedsApp()
