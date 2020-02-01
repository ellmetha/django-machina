"""
    Forum search forms
    ==================

    This module defines forms provided by the ``forum_search`` application.

"""

from django import forms
from django.utils.translation import ugettext_lazy as _
from haystack.forms import FacetedSearchForm
from haystack.inputs import AutoQuery

from machina.core.db.models import get_model
from machina.core.loading import get_class
from machina.conf import settings

if settings.SEARCH_ENGINE == 'postgres':
    from django.contrib.postgres.search import SearchQuery, SearchRank
    from django.db.models import F

Forum = get_model('forum', 'Forum')

Post = get_model('forum_conversation', 'Post')

PermissionHandler = get_class('forum_permission.handler', 'PermissionHandler')


class SearchForm(FacetedSearchForm):
    """ Allows to search forum topics and posts. """

    search_topics = forms.BooleanField(label=_('Search only in topic subjects'), required=False)

    search_poster_name = forms.CharField(
        label=_('Search for poster'),
        help_text=_('Enter a user name to limit the search to a specific user.'),
        max_length=255, required=False,
    )

    search_forums = forms.MultipleChoiceField(
        label=_('Search in specific forums'),
        help_text=_('Select the forums you wish to search in.'),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)

        super().__init__(*args, **kwargs)

        # Update some fields
        self.fields['q'].label = _('Search for keywords')
        self.fields['q'].widget.attrs['placeholder'] = _('Keywords or phrase')
        self.fields['search_poster_name'].widget.attrs['placeholder'] = _('Poster name')

        self.allowed_forums = PermissionHandler().get_readable_forums(Forum.objects.all(), user)
        if self.allowed_forums:
            self.fields['search_forums'].choices = [
                (f.id, '{} {}'.format('-' * f.margin_level, f.name)) for f in self.allowed_forums
            ]
        else:
            # The user cannot view any single forum, the 'search_forums' field can be deleted
            del self.fields['search_forums']

    def search(self):
        sqs = super().search()

        if not self.is_valid():
            return self.no_query_found()

        # Handles topic-based searches
        if self.cleaned_data['search_topics']:
            sqs = sqs.filter(topic_subject=AutoQuery(self.cleaned_data['q']))

        # Handles searches by poster name
        if self.cleaned_data['search_poster_name']:
            sqs = sqs.filter(poster_name__icontains=self.cleaned_data['search_poster_name'])

        # Handles searches in specific forums if necessary
        if 'search_forums' in self.cleaned_data and self.cleaned_data['search_forums']:
            sqs = sqs.filter(forum__in=self.cleaned_data['search_forums'])
        else:
            forum_ids = self.allowed_forums.values_list('id', flat=True)
            sqs = sqs.filter(forum__in=forum_ids) if forum_ids else sqs.none()

        return sqs


class PostgresSearchForm(forms.Form):
    q = forms.CharField(required=False, label=_('Search'),
                        widget=forms.TextInput(attrs={'type': 'search'}))

    search_topics = forms.BooleanField(label=_('Search only in topic subjects'), required=False)

    search_poster_name = forms.CharField(
        label=_('Search for poster'),
        help_text=_('Enter a user name to limit the search to a specific user.'),
        max_length=255, required=False,
    )

    search_forums = forms.MultipleChoiceField(
        label=_('Search in specific forums'),
        help_text=_('Select the forums you wish to search in.'),
        required=False,
    )

    def __init__(self, request):
        user = request.user

        super().__init__(request.GET)

        # Update some fields
        self.fields['q'].label = _('Search for keywords')
        self.fields['q'].widget.attrs['placeholder'] = _('Keywords or phrase')
        self.fields['search_poster_name'].widget.attrs['placeholder'] = _('Poster name')

        self.allowed_forums = PermissionHandler().get_readable_forums(Forum.objects.all(), user)
        if self.allowed_forums:
            self.fields['search_forums'].choices = [
                (f.id, '{} {}'.format('-' * f.margin_level, f.name)) for f in self.allowed_forums
            ]
        else:
            # The user cannot view any single forum, the 'search_forums' field can be deleted
            del self.fields['search_forums']

    def no_query_found(self):
        return None

    def search(self):

        if not self.is_valid():
            return self.no_query_found()

        if not self.cleaned_data.get('q'):
            return self.no_query_found()

        query = SearchQuery(self.cleaned_data['q'])

        if self.cleaned_data['search_topics']:
            sqs = Post.objects.annotate(rank=SearchRank(F('search_vector_subject'), query))
            sqs = sqs.filter(search_vector_subject=query)
        else:
            sqs = Post.objects.annotate(rank=SearchRank(F('search_vector_all'), query))
            sqs = sqs.filter(search_vector_all=query)

        sqs = sqs.order_by('-rank')

        if self.cleaned_data['search_poster_name']:
            sqs = sqs.filter(poster__username__icontains=self.cleaned_data['search_poster_name'])

        if 'search_forums' in self.cleaned_data and self.cleaned_data['search_forums']:
            sqs = sqs.filter(topic__forum__in=self.cleaned_data['search_forums'])
        else:
            forum_ids = self.allowed_forums.values_list('id', flat=True)

            if self.allowed_forums.values_list('id', flat=True):
                sqs = sqs.filter(topic__forum__in=forum_ids)
            else:
                sqs = None

        return sqs[:20000]  # without this split we can get 502 on some requests
