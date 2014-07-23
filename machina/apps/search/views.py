# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from haystack import views

# Local application / specific library imports


class FacetedSearchView(views.FacetedSearchView):
    def build_form(self):
        form = super(self.__class__, self).build_form(form_kwargs={'user': self.request.user})
        return form
