"""
    Forum member URLs
    =================

    This module defines URL patterns associated with the django-machina's ``forum_member``
    application.

"""

from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from machina.core.loading import get_class
from machina.core.urls import URLPatternsFactory


class ForumMemberURLPatternsFactory(URLPatternsFactory):
    """ Allows to generate the URL patterns of the ``forum_member`` application. """

    app_namespace = 'forum_member'

    user_posts_list = get_class('forum_member.views', 'UserPostsView')
    forum_profile_detail_view = get_class('forum_member.views', 'ForumProfileDetailView')
    forum_profile_update_view = get_class('forum_member.views', 'ForumProfileUpdateView')
    topic_subscribe_view = get_class('forum_member.views', 'TopicSubscribeView')
    topic_unsubscribe_view = get_class('forum_member.views', 'TopicUnsubscribeView')
    topic_subscription_list_view = get_class('forum_member.views', 'TopicSubscriptionListView')

    def get_urlpatterns(self):
        """ Returns the URL patterns managed by the considered factory / application. """
        return [
            url(
                _(r'^profile/edit/$'),
                self.forum_profile_update_view.as_view(),
                name='profile_update',
            ),
            url(
                _(r'^profile/(?P<pk>[\w-]+)/$'),
                self.forum_profile_detail_view.as_view(),
                name='profile',
            ),
            url(
                _(r'^profile/(?P<pk>[\w-]+)/posts/$'),
                self.user_posts_list.as_view(),
                name='user_posts',
            ),
            url(
                _(r'^subscriptions/$'),
                self.topic_subscription_list_view.as_view(),
                name='user_subscriptions',
            ),
            url(
                _(r'^topic/(?P<pk>\d+)/subscribe/$'),
                self.topic_subscribe_view.as_view(),
                name='topic_subscribe',
            ),
            url(
                _(r'^topic/(?P<pk>\d+)/unsubscribe/$'),
                self.topic_unsubscribe_view.as_view(),
                name='topic_unsubscribe',
            ),
        ]


urlpatterns_factory = ForumMemberURLPatternsFactory()
