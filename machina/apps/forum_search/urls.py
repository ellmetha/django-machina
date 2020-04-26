"""
    Forum search URLs
    =================

    This module defines URL patterns associated with the django-machina's ``forum_search``
    application.

"""

from django.urls import path

from machina.core.loading import get_class
from machina.core.urls import URLPatternsFactory


class ForumSearchURLPatternsFactory(URLPatternsFactory):
    """ Allows to generate the URL patterns of the ``forum_search`` application. """

    app_namespace = 'forum_search'

    search_view = get_class('forum_search.views', 'PostgresSearchView')
    search_path = path('', search_view.as_view(), name='search')

    def get_urlpatterns(self):
        """ Returns the URL patterns managed by the considered factory / application. """
        return [self.search_path, ]


urlpatterns_factory = ForumSearchURLPatternsFactory()
