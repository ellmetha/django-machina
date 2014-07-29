# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django import forms
from django.db.models import get_model
from django.utils.translation import ugettext_lazy as _
from haystack.forms import FacetedSearchForm

# Local application / specific library imports
from machina.core.loading import get_class

Forum = get_model('forum', 'Forum')

PermissionHandler = get_class('permission.handler', 'PermissionHandler')
perm_handler = PermissionHandler()


class SearchForm(FacetedSearchForm):
    search_poster_name = forms.CharField(
        label=_('Search for poster'), help_text=_('Enter a user name to limit the search to a specific user.'),
        max_length=255, required=False)

    search_forums = forms.MultipleChoiceField(
        label=_('Search in specific forums'), help_text=_('Select the forums you wish to search in.'),
        required=False)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(SearchForm, self).__init__(*args, **kwargs)
        # Update some fields
        self.fields['q'].label = _('Search for keywords')
        self.fields['q'].widget.attrs['placeholder'] = _('Keywords or phrase')
        self.fields['search_poster_name'].widget.attrs['placeholder'] = _('Poster name')
        self.fields['search_forums'].choices = [(f.id, '{} {}'.format('-' * f.margin_level, f.name)) for f in perm_handler.forum_list_filter(Forum.objects.all(), user)]

    def search(self):
        sqs = super(SearchForm, self).search()

        if not self.is_valid():
            return self.no_query_found()

        # Handles searches by poster name
        if self.cleaned_data['search_poster_name']:
            sqs = sqs.filter(poster_name__icontains=self.cleaned_data['search_poster_name'])

        # Handles searches in specific forums
        if self.cleaned_data['search_forums']:
            sqs = sqs.filter(forum__in=self.cleaned_data['search_forums'])

        return sqs