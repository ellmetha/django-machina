# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.conf.urls import include
from django.conf.urls import patterns
from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

# Local application / specific library imports
from machina.apps.conversation import views
from machina.apps.conversation.polls.app import application as polls_app
from machina.core.app import Application


class BaseConversationApp(Application):
    name = 'conversation'

    topic_view = views.TopicView
    topic_create_view = views.TopicCreateView
    topic_update_view = views.TopicUpdateView
    post_create_view = views.PostCreateView
    post_update_view = views.PostUpdateView
    post_delete_view = views.PostDeleteView

    def get_urls(self):
        urls = super(BaseConversationApp, self).get_urls()
        urls += [
            url(_(r'^topic/(?P<pk>\d+)/$'), self.topic_view.as_view(), name='topic'),
            url(_(r'^forum/(?P<forum_pk>\d+)/topic/(?P<pk>\d+)/$'), self.topic_view.as_view(), name='topic'),
            url(_(r'^forum/(?P<forum_pk>\d+)/topic/create/$'), self.topic_create_view.as_view(), name='topic-create'),
            url(_(r'^forum/(?P<forum_pk>\d+)/topic/(?P<pk>\d+)/update/$'), self.topic_update_view.as_view(), name='topic-update'),
            url(_(r'^forum/(?P<forum_pk>\d+)/topic/(?P<topic_pk>\d+)/post/create/$'), self.post_create_view.as_view(), name='post-create'),
            url(_(r'^forum/(?P<forum_pk>\d+)/topic/(?P<topic_pk>\d+)/(?P<pk>\d+)/post/update/$'), self.post_update_view.as_view(), name='post-update'),
            url(_(r'^forum/(?P<forum_pk>\d+)/topic/(?P<topic_pk>\d+)/(?P<pk>\d+)/post/delete/$'), self.post_delete_view.as_view(), name='post-delete'),
        ]
        return patterns('', *urls)


class PollsApp(Application):
    name = None
    polls_app = polls_app

    def get_urls(self):
        urls = super(PollsApp, self).get_urls()
        urls += [
            url(_(r'^forum/(?P<forum_pk>\d+)/topic/(?P<topic_pk>\d+)/'),
                include(self.polls_app.urls)),
        ]
        return patterns('', *urls)


class ConversationApp(BaseConversationApp, PollsApp):
    """
    Composite class combining Conversation views with Polls views.
    """


application = ConversationApp()
