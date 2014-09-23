# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django import template

# Local application / specific library imports
from machina.core.loading import get_class

PermissionHandler = get_class('permission.handler', 'PermissionHandler')
perm_handler = PermissionHandler()

register = template.Library()


@register.filter
def has_content_downloadable_by(post, user):
    """
    This will return a boolean indicating if the passed post has attachments that
    can be downloaded by the given user.

    Usage::

        {% if post|has_content_downloadable_by:user %}...{% endif %}
    """
    return perm_handler.can_download_files(post.topic.forum, user)
