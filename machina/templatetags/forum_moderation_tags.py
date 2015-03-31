# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import unicode_literals

# Third party imports
from django import template

# Local application / specific library imports
from machina.core.loading import get_class

PermissionHandler = get_class('forum_permission.handler', 'PermissionHandler')
perm_handler = PermissionHandler()

register = template.Library()


@register.filter
def can_access_moderation_panel(user):
    """
    This will return a boolean indicating if the passed user can access
    the forum moderation panel.

    Usage::

        {% if user|can_access_moderation_panel %}...{% endif %}
    """
    return perm_handler.can_access_moderation_panel(user)
