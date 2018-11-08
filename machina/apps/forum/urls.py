"""
    Forum URLs
    ==========

    This module defines URL patterns associated with the django-machina's ``forum`` application.

"""

from django.urls import path
from django.utils.translation import ugettext_lazy as _

from machina.core.loading import get_class
from machina.core.urls import URLPatternsFactory


class ForumURLPatternsFactory(URLPatternsFactory):
    """ Allows to generate the URL patterns of the ``forum`` application. """

    app_namespace = 'forum'

    index_view = get_class('forum.views', 'IndexView')
    forum_view = get_class('forum.views', 'ForumView')

    def get_urlpatterns(self):
        """ Returns the URL patterns managed by the considered factory / application. """
        return [
            path('', self.index_view.as_view(), name='index'),
            path(
                _('forum/<slug>-<pk>/'),
                self.forum_view.as_view(),
                name='forum',
            ),
        ]


urlpatterns_factory = ForumURLPatternsFactory()
