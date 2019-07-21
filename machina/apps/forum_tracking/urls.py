"""
    Forum tracking URLs
    ===================

    This module defines URL patterns associated with the django-machina's ``forum_tracking``
    application.

"""

from django.urls import path

from machina.core.loading import get_class
from machina.core.urls import URLPatternsFactory


class ForumTrackingURLPatternsFactory(URLPatternsFactory):
    """ Allows to generate the URL patterns of the ``forum_search`` application. """

    app_namespace = 'forum_tracking'

    mark_forums_read_view = get_class('forum_tracking.views', 'MarkForumsReadView')
    mark_topics_read_view = get_class('forum_tracking.views', 'MarkTopicsReadView')
    unread_topics_view = get_class('forum_tracking.views', 'UnreadTopicsView')

    def get_urlpatterns(self):
        """ Returns the URL patterns managed by the considered factory / application. """
        return [
            path(
                'mark/forums/',
                self.mark_forums_read_view.as_view(),
                name='mark_all_forums_read',
            ),
            path(
                'mark/forums/<int:pk>/',
                self.mark_forums_read_view.as_view(),
                name='mark_subforums_read',
            ),
            path(
                'mark/forum/<int:pk>/topics/',
                self.mark_topics_read_view.as_view(),
                name='mark_topics_read',
            ),
            path(
                'unread-topics/',
                self.unread_topics_view.as_view(),
                name='unread_topics',
            ),
        ]


urlpatterns_factory = ForumTrackingURLPatternsFactory()
