# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.conf.urls import patterns
from django.conf.urls import url
from haystack.views import search_view_factory

# Local application / specific library imports
from machina.core.app import Application
from machina.core.loading import get_class


class SearchApp(Application):
    name = 'forum_search'

    search_view = get_class('forum_search.views', 'FacetedSearchView')
    search_form = get_class('forum_search.forms', 'SearchForm')

    def get_urls(self):
        urls = [
            url(r'^$', search_view_factory(
                view_class=self.search_view,
                form_class=self.search_form),
                name='search'),
        ]
        return patterns('', *urls)


application = SearchApp()
