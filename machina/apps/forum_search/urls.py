"""
    Forum search URLs
    =================

    This module defines URL patterns associated with the django-machina's ``forum_search``
    application.

"""

from django.urls import path
from haystack.views import search_view_factory

from machina.core.loading import get_class
from machina.core.urls import URLPatternsFactory


class ForumSearchURLPatternsFactory(URLPatternsFactory):
    """ Allows to generate the URL patterns of the ``forum_search`` application. """

    app_namespace = 'forum_search'

    search_view = get_class('forum_search.views', 'FacetedSearchView')
    search_form = get_class('forum_search.forms', 'SearchForm')

    def get_urlpatterns(self):
        """ Returns the URL patterns managed by the considered factory / application. """
        return [
            path(
                '',
                search_view_factory(view_class=self.search_view, form_class=self.search_form),
                name='search',
            ),
        ]


urlpatterns_factory = ForumSearchURLPatternsFactory()
