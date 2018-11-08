"""
    Forum member URLs
    =================

    This module defines URL patterns associated with the django-machina's ``forum_member``
    application.

"""

from django.urls import path
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
            path(
                _('profile/<pk>/'),
                self.forum_profile_detail_view.as_view(),
                name='profile',
            ),
            path(
                _('profile/<pk>/posts/'),
                self.user_posts_list.as_view(),
                name='user_posts',
            ),
            path(
                _('profile/edit/'),
                self.forum_profile_update_view.as_view(),
                name='profile_update',
            ),
            path(
                _('subscriptions/'),
                self.topic_subscription_list_view.as_view(),
                name='user_subscriptions',
            ),
            path(
                _('topic/<pk>/subscribe/'),
                self.topic_subscribe_view.as_view(),
                name='topic_subscribe',
            ),
            path(
                _('topic/<pk>/unsubscribe/'),
                self.topic_unsubscribe_view.as_view(),
                name='topic_unsubscribe',
            ),
        ]


urlpatterns_factory = ForumMemberURLPatternsFactory()
