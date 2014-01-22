# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import unicode_literals

# Third party imports
from django import template
from django.db.models import get_model

# Local application / specific library imports
from machina.core.loading import get_class

Forum = get_model('forum', 'Forum')

PermissionHandler = get_class('permission.handler', 'PermissionHandler')
perm_handler = PermissionHandler()

register = template.Library()


@register.assignment_tag
def get_forum_last_post(forum, user):
    """
    This will return the last post that can be read by the passed user (permissions check).

    Usage::

        {% get_forum_last_post forum request.user as var %}
    """
    # Retrieve the last post link associated with the current forum
    last_post = perm_handler.get_forum_last_post(forum, user)
    return last_post
