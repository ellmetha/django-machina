from haystack import views


class FacetedSearchView(views.FacetedSearchView):
    """
    Allows to search within forums
    """
    template = 'forum_search/search.html'

    def build_form(self):
        form = super().build_form(form_kwargs={'user': self.request.user})
        return form
