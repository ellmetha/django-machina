# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import unicode_literals

# Third party imports
# Local application / specific library imports
from machina.core.loading import get_class

PermissionHandler = get_class('forum_permission.handler', 'PermissionHandler')


class ForumPermissionHandlerMiddleware(object):
    """
    This middleware attach to each request an instance of the PermissionHandler.
    This allows to cache the permissions granted for the current user for the lifetime
    of the request object.
    """
    def process_request(self, request):
        request.forum_permission_handler = PermissionHandler()
