# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
# Local application / specific library imports


class Application(object):
    """
    Machina's views and URLs use a tree of 'app' instances, each of which subclass this Application
    class and provide an 'urls' property.
    This process is directly inspired from the one provided by django-oscar.
    """
    name = None
    # Default permission for any view not in permissions_map
    default_permissions = None
    # Maps view names to a tuple or list of permissions
    permissions_map = {}

    def __init__(self, app_name=None, **kwargs):
        self.app_name = app_name
        # Set all kwargs as object attributes
        for key, value in kwargs.iteritems():
            setattr(self, key, value)

    def get_urls(self):
        """
        Return the url patterns for the considered app. It must be implemented in
        any subclass.
        """
        raise NotImplementedError

    @property
    def urls(self):
        # We set the application and instance namespace here
        return self.get_urls(), self.app_name, self.name
