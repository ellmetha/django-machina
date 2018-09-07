"""
    Machina core URL helpers
    ========================

    This module defines commons URLs helpers and abstractions used by django-machina to manage its
    URL patterns.

"""


class URLPatternsFactory:
    """ Allows to generate the URL patterns of a machina application.

    Machina's views and URLs use a tree of ``URLPatternsFactory`` instances in order to build the
    complete list of URL patterns of the forum application. This class provides a
    ``get_urlpatterns`` method that allows to define the URL patterns to include in the global list
    of URLs associated with the forum application. This behavior allows to easily override each of
    the views used to build the final list of URL patterns (because the views are imported
    dynamically). It also allows to append additional URLs to the generated URL patterns by
    subclassing the ``URLPatternsFactory`` subclass associated with the considered forum app.

    """

    app_namespace = None

    def get_urlpatterns(self):
        """ Returns the URL patterns managed by the considered factory / application.

        This method should be implemented in any subclass.
        """
        return []

    @property
    def urlpatterns(self):
        """ Returns a tuple containing the list of URL patterns and an app namespace. """
        return self.get_urlpatterns(), self.app_namespace
