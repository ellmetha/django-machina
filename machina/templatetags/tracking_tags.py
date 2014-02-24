# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import unicode_literals

# Third party imports
from django import template
from django.db.models import get_model

# Local application / specific library imports
from machina.core.loading import get_class

Forum = get_model('forum', 'Forum')
ForumReadTrack = get_model('tracking', 'ForumReadTrack')

PermissionHandler = get_class('permission.handler', 'PermissionHandler')
perm_handler = PermissionHandler()

register = template.Library()


@register.assignment_tag
def get_unread_forums(from_level, user):
    """
    This will return a list of unread forums for the given user from a given level in the forums tree.

    Usage::

        {% get_unread_forums 0 request.user as unread_forums %}
    """
    unread_forums = []

    # A user which is not authenticated will never see a forum as unread
    if not user.is_authenticated():
        return unread_forums

    forums = Forum.objects.filter(level=from_level)
    for forum in forums:
        if forum not in unread_forums:
            readable_forums = perm_handler.forum_list_filter(
                forum.get_descendants(include_self=True), user)
            unread = ForumReadTrack.objects.get_unread_forums_from_list(readable_forums, user)
            unread_forums.extend(unread)

    return unread_forums
