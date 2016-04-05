# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import include
from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from machina.apps.forum_conversation.forum_attachments.app import application as attachments_app
from machina.apps.forum_conversation.forum_polls.app import application as polls_app
from machina.core.app import Application
from machina.core.loading import get_class


class BaseConversationApp(Application):
    name = 'forum_conversation'

    topic_view = get_class('forum_conversation.views', 'TopicView')
    topic_create_view = get_class('forum_conversation.views', 'TopicCreateView')
    topic_update_view = get_class('forum_conversation.views', 'TopicUpdateView')
    post_create_view = get_class('forum_conversation.views', 'PostCreateView')
    post_update_view = get_class('forum_conversation.views', 'PostUpdateView')
    post_delete_view = get_class('forum_conversation.views', 'PostDeleteView')

    def get_urls(self):
        urls = super(BaseConversationApp, self).get_urls()

        conversation_patterns = [
            url(_(r'^topic/(?P<slug>[\w-]+)-(?P<pk>\d+)/$'),
                self.topic_view.as_view(), name='topic'),

            url(_(r'^topic/create/$'), self.topic_create_view.as_view(), name='topic_create'),
            url(_(r'^topic/(?P<slug>[\w-]+)-(?P<pk>\d+)/update/$'),
                self.topic_update_view.as_view(), name='topic_update'),

            url(_(r'^topic/(?P<topic_slug>[\w-]+)-(?P<topic_pk>\d+)/post/create/$'),
                self.post_create_view.as_view(), name='post_create'),
            url(_(r'^topic/(?P<topic_slug>[\w-]+)-(?P<topic_pk>\d+)/(?P<pk>\d+)/post/update/$'),
                self.post_update_view.as_view(), name='post_update'),
            url(_(r'^topic/(?P<topic_slug>[\w-]+)-(?P<topic_pk>\d+)/(?P<pk>\d+)/post/delete/$'),
                self.post_delete_view.as_view(), name='post_delete'),
        ]

        urls += [
            url(_(r'forum/(?P<forum_slug>[\w-]+)-(?P<forum_pk>\d+)/'),
                include(conversation_patterns)),
        ]
        return urls


class PollsApp(Application):
    name = None
    polls_app = polls_app

    def get_urls(self):
        urls = super(PollsApp, self).get_urls()
        urls += [
            url(r'^', include(self.polls_app.urls)),
        ]
        return urls


class AttachmentsApp(Application):
    name = None
    attachments_app = attachments_app

    def get_urls(self):
        urls = super(AttachmentsApp, self).get_urls()
        urls += [
            url(r'^', include(self.attachments_app.urls)),
        ]
        return urls


class ConversationApp(BaseConversationApp, PollsApp, AttachmentsApp):
    """
    Composite class combining Conversation views with Polls views and Attachments views.
    """


application = ConversationApp()
