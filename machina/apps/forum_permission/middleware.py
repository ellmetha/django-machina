# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import unicode_literals

# Third party imports
# Local application / specific library imports
from machina.core.loading import get_class

PermissionHandler = get_class('forum_permission.handler', 'PermissionHandler')


class ForumPermissionHandlerMiddleware(object):
    def process_request(self, request):
        request.forum_permission_handler = PermissionHandler()
