# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from haystack import views


class FacetedSearchView(views.FacetedSearchView):
    """
    Allows to search within forums
    """
    template = 'forum_search/search.html'

    def build_form(self):
        form = super(self.__class__, self).build_form(form_kwargs={'user': self.request.user})
        return form
