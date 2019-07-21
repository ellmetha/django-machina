"""
    Forum moderation URLs
    =====================

    This module defines URL patterns associated with the django-machina's ``forum_moderation``
    application.

"""

from django.urls import path

from machina.core.loading import get_class
from machina.core.urls import URLPatternsFactory


class ForumModerationURLPatternsFactory(URLPatternsFactory):
    """ Allows to generate the URL patterns of the ``forum_moderation`` application. """

    app_namespace = 'forum_moderation'

    topic_lock_view = get_class('forum_moderation.views', 'TopicLockView')
    topic_unlock_view = get_class('forum_moderation.views', 'TopicUnlockView')
    topic_delete_view = get_class('forum_moderation.views', 'TopicDeleteView')
    topic_move_view = get_class('forum_moderation.views', 'TopicMoveView')
    topic_update_to_normal_topic_view = get_class(
        'forum_moderation.views', 'TopicUpdateToNormalTopicView',
    )
    topic_update_to_sticky_topic_view = get_class(
        'forum_moderation.views', 'TopicUpdateToStickyTopicView',
    )
    topic_update_to_announce_view = get_class('forum_moderation.views', 'TopicUpdateToAnnounceView')
    moderation_queue_list_view = get_class('forum_moderation.views', 'ModerationQueueListView')
    moderation_queue_detail_view = get_class('forum_moderation.views', 'ModerationQueueDetailView')
    post_approve_view = get_class('forum_moderation.views', 'PostApproveView')
    post_disapprove_view = get_class('forum_moderation.views', 'PostDisapproveView')

    def get_urlpatterns(self):
        """ Returns the URL patterns managed by the considered factory / application. """
        return [
            path(
                'topic/<str:slug>-<int:pk>/lock/',
                self.topic_lock_view.as_view(),
                name='topic_lock',
            ),
            path(
                'topic/<str:slug>-<int:pk>/unlock/',
                self.topic_unlock_view.as_view(),
                name='topic_unlock',
            ),
            path(
                'topic/<str:slug>-<int:pk>/delete/',
                self.topic_delete_view.as_view(),
                name='topic_delete',
            ),
            path(
                'topic/<str:slug>-<int:pk>/move/',
                self.topic_move_view.as_view(),
                name='topic_move',
            ),
            path(
                'topic/<str:slug>-<int:pk>/change/topic/',
                self.topic_update_to_normal_topic_view.as_view(),
                name='topic_update_to_post',
            ),
            path(
                'topic/<str:slug>-<int:pk>/change/sticky/',
                self.topic_update_to_sticky_topic_view.as_view(),
                name='topic_update_to_sticky',
            ),
            path(
                'topic/<str:slug>-<int:pk>/change/announce/',
                self.topic_update_to_announce_view.as_view(),
                name='topic_update_to_announce',
            ),
            path('queue/', self.moderation_queue_list_view.as_view(), name='queue'),
            path(
                'queue/<int:pk>/',
                self.moderation_queue_detail_view.as_view(),
                name='queued_post',
            ),
            path(
                'queue/<int:pk>/approve/',
                self.post_approve_view.as_view(),
                name='approve_queued_post',
            ),
            path(
                'queue/<int:pk>/disapprove/',
                self.post_disapprove_view.as_view(),
                name='disapprove_queued_post',
            ),
        ]


urlpatterns_factory = ForumModerationURLPatternsFactory()
