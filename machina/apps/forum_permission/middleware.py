# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import uuid

from machina.core.loading import get_class

PermissionHandler = get_class('forum_permission.handler', 'PermissionHandler')


class ForumPermissionMiddleware(object):
    """
    This middleware attaches an instance of the PermissionHandler to each request.
    This allows to cache the permissions for the lifetime of the request object.
    The middleware also attaches a random identifier to each anonymous user in order
    to perform proper permission checks for anonymous users. This identifier is
    stored in the session.
    """
    anonymous_forum_key_session_id = '_anonymous_forum_key'

    def process_request(self, request):
        if not request.user.is_authenticated():
            # Get the anonymous forum key and attaches it the AnonymousUser instance.
            anonymous_forum_key = request.session.get(self.anonymous_forum_key_session_id, None)
            if anonymous_forum_key is None:
                anonymous_forum_key = self.get_anonymous_forum_key()
                request.session[self.anonymous_forum_key_session_id] = anonymous_forum_key

            setattr(request.user, 'forum_key', anonymous_forum_key)

        request.forum_permission_handler = PermissionHandler()

    def get_anonymous_forum_key(self):
        """
        Returns a random anonymous forum key.
        """
        return uuid.uuid4().hex
