"""
    Forum search views
    ==================

    This module defines views provided by the ``forum_search`` application.

"""

from django.core.paginator import Paginator
from django.shortcuts import render
from django.views import View
from machina.apps.forum_search.forms import PostgresSearchForm
from machina.conf import settings
from haystack import views


class FacetedSearchView(views.FacetedSearchView):
    """ Allows to search within forums. """

    template = 'forum_search/search.html'

    def build_form(self):
        form = super().build_form(form_kwargs={'user': self.request.user})
        return form


class PostgresSearchView(View):
    """ Allows to search using postgres search. """

    form_class = PostgresSearchForm
    template = 'forum_search/postgres_search.html'

    def get(self, request, *args, **kwargs):

        form = self.form_class(request)

        if 'q' in request.GET:
            result = form.search()
            paginator = Paginator(result, settings.TOPIC_POSTS_NUMBER_PER_PAGE)
            page_num = request.GET['page'] if 'page' in request.GET else 1
            page = paginator.page(page_num)
            context = {
                'form': form,
                'result_count': len(result),
                'query': form.cleaned_data.get('q'),
                'page': page,
                'paginator': paginator,
            }
        else:
            context = {
                'form': form,
                'query': False,
            }

        return render(request, self.template, context)

    def post(self, request, *args, **kwargs):
        self.get(request, *args, **kwargs)
