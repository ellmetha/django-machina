"""
    Forum conversation URLs
    =======================

    This module defines URL patterns associated with the django-machina's ``forum_conversation``
    application.

"""

from django.conf.urls import include, url
from django.utils.translation import ugettext_lazy as _

from machina.apps.forum_conversation.forum_attachments.urls import \
    urlpatterns_factory as attachments_urlpatterns_factory
from machina.apps.forum_conversation.forum_polls.urls import \
    urlpatterns_factory as polls_urlpatterns_factory
from machina.core.loading import get_class
from machina.core.urls import URLPatternsFactory


class BaseForumConversationURLPatternsFactory(URLPatternsFactory):
    """ Allows to generate the URL patterns of the ``forum_conversation`` application. """

    app_namespace = 'forum_conversation'

    topic_view = get_class('forum_conversation.views', 'TopicView')
    topic_create_view = get_class('forum_conversation.views', 'TopicCreateView')
    topic_update_view = get_class('forum_conversation.views', 'TopicUpdateView')
    post_create_view = get_class('forum_conversation.views', 'PostCreateView')
    post_update_view = get_class('forum_conversation.views', 'PostUpdateView')
    post_delete_view = get_class('forum_conversation.views', 'PostDeleteView')

    def get_urlpatterns(self):
        """ Returns the URL patterns managed by the considered factory / application. """
        urlpatterns = super().get_urlpatterns()

        conversation_urlpatterns = [
            url(
                _(r'^topic/(?P<slug>[\w-]+)-(?P<pk>\d+)/$'),
                self.topic_view.as_view(),
                name='topic',
            ),

            url(_(r'^topic/create/$'), self.topic_create_view.as_view(), name='topic_create'),
            url(
                _(r'^topic/(?P<slug>[\w-]+)-(?P<pk>\d+)/update/$'),
                self.topic_update_view.as_view(),
                name='topic_update',
            ),

            url(
                _(r'^topic/(?P<topic_slug>[\w-]+)-(?P<topic_pk>\d+)/post/create/$'),
                self.post_create_view.as_view(),
                name='post_create',
            ),
            url(
                _(r'^topic/(?P<topic_slug>[\w-]+)-(?P<topic_pk>\d+)/(?P<pk>\d+)/post/update/$'),
                self.post_update_view.as_view(),
                name='post_update',
            ),
            url(_(r'^topic/(?P<topic_slug>[\w-]+)-(?P<topic_pk>\d+)/(?P<pk>\d+)/post/delete/$'),
                self.post_delete_view.as_view(), name='post_delete'),
        ]

        urlpatterns += [
            url(
                _(r'forum/(?P<forum_slug>[\w-]+)-(?P<forum_pk>\d+)/'),
                include(conversation_urlpatterns),
            ),
        ]

        return urlpatterns


class ForumAttachmentsURLPatternsFactory(URLPatternsFactory):
    """ Allows to generate the URL patterns of the ``forum_attachments`` application. """

    attachments_urlpatterns_factory = attachments_urlpatterns_factory

    def get_urlpatterns(self):
        """ Returns the URL patterns managed by the considered factory / application. """
        return super().get_urlpatterns() + [
            url(r'^', include(self.attachments_urlpatterns_factory.urlpatterns)),
        ]


class ForumPollsURLPatternsFactory(URLPatternsFactory):
    """ Allows to generate the URL patterns of the ``forum_attachments`` application. """

    polls_urlpatterns_factory = polls_urlpatterns_factory

    def get_urlpatterns(self):
        """ Returns the URL patterns managed by the considered factory / application. """
        return super().get_urlpatterns() + [
            url(r'^', include(self.polls_urlpatterns_factory.urlpatterns)),
        ]


class ForumConversationURLPatternsFactory(
    BaseForumConversationURLPatternsFactory, ForumAttachmentsURLPatternsFactory,
    ForumPollsURLPatternsFactory,
):
    """ Composite class combining conversation views with polls & attachments views. """


urlpatterns_factory = ForumConversationURLPatternsFactory()
