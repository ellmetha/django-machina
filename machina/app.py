# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import include
from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from machina.core.app import Application
from machina.core.loading import get_class


class BoardApp(Application):
    name = None

    forum_app = get_class('forum.app', 'application')
    conversation_app = get_class('forum_conversation.app', 'application')
    feeds_app = get_class('forum_feeds.app', 'application')
    member_app = get_class('forum_member.app', 'application')
    moderation_app = get_class('forum_moderation.app', 'application')
    search_app = get_class('forum_search.app', 'application')
    tracking_app = get_class('forum_tracking.app', 'application')

    def get_urls(self):
        urls = [
            url(r'', include(self.forum_app.urls)),
            url(r'', include(self.conversation_app.urls)),
            url(_(r'^feeds/'), include(self.feeds_app.urls)),
            url(_(r'^member/'), include(self.member_app.urls)),
            url(_(r'^moderation/'), include(self.moderation_app.urls)),
            url(_(r'^search/'), include(self.search_app.urls)),
            url(_(r'^tracking/'), include(self.tracking_app.urls)),
        ]
        return urls


board = forum = application = BoardApp()
