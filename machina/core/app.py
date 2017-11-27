# -*- coding: utf-8 -*-

from __future__ import unicode_literals


class Application(object):
    """
    Machina's views and URLs use a tree of 'app' instances, each of which subclass this Application
    class and provide an 'urls' property.
    This process is directly inspired from the one provided by django-oscar.
    """
    name = None

    def __init__(self, **kwargs):
        # Set all kwargs as object attributes
        for key, value in kwargs.items():  # pragma: no cover
            setattr(self, key, value)

    def get_urls(self):
        """
        Return the url patterns for the considered app. It should be implemented in
        any subclass.
        """
        return []

    @property
    def urls(self):
        # We set the application and instance namespaces here
        return self.get_urls(), self.name
