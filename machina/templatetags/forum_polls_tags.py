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
def has_been_completed_by(poll, user):
    """
    This will return a boolean indicating if the passed user has already
    voted in the given poll.

    Usage::

        {% if poll|has_been_completed_by:user %}...{% endif %}
    """
    user_votes = user.poll_votes.filter(poll_option__poll=poll)
    return user_votes.exists()
