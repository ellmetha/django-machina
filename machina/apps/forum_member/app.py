# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from machina.core.app import Application
from machina.core.loading import get_class


class MemberApp(Application):
    name = 'forum_member'

    user_topics_view = get_class('forum_member.views', 'UserTopicsView')
    forum_profile_detail_view = get_class('forum_member.views', 'ForumProfileDetailView')
    forum_profile_update_view = get_class('forum_member.views', 'ForumProfileUpdateView')
    topic_subscribe_view = get_class('forum_member.views', 'TopicSubscribeView')
    topic_unsubscribe_view = get_class('forum_member.views', 'TopicUnsubscribeView')

    def get_urls(self):
        return [
            url(_(r'^profile/(?P<pk>\d+)/$'),
                self.forum_profile_detail_view.as_view(), name='profile'),
            url(_(r'^profile/edit/$'),
                self.forum_profile_update_view.as_view(), name='profile_update'),
            url(_(r'^ego/topics/$'), self.user_topics_view.as_view(), name='user_topics'),
            url(_(r'^topic/(?P<pk>\d+)/subscribe/$'),
                self.topic_subscribe_view.as_view(), name='topic_subscribe'),
            url(_(r'^topic/(?P<pk>\d+)/unsubscribe/$'),
                self.topic_unsubscribe_view.as_view(), name='topic_unsubscribe'),
        ]


application = MemberApp()
