# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django import forms
from django.utils.translation import ugettext_lazy as _
from haystack.forms import FacetedSearchForm

# Local application / specific library imports


class SearchForm(FacetedSearchForm):
    search_poster_name = forms.CharField(
        label=_('Search for poster'), help_text=_('Enter a user name to limit the search to a specific user.'),
        max_length=255, required=False)

    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)

        # Update some fields
        self.fields['q'].label = _('Search for keywords')
        self.fields['q'].widget.attrs['placeholder'] = _('Keywords or phrase')
        self.fields['search_poster_name'].widget.attrs['placeholder'] = _('Poster name')

    def search(self):
        sqs = super(SearchForm, self).search()

        if not self.is_valid():
            return self.no_query_found()

        # Handles searches by poster name
        if self.cleaned_data['search_poster_name']:
            sqs = sqs.filter(poster_name__icontains=self.cleaned_data['search_poster_name'])

        return sqs
