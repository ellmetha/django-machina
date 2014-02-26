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
def get_unread_forums(forums, user):
    """
    This will return a list of unread forums for the given user from a given set of forums.

    Usage::

        {% get_unread_forums forums request.user as unread_forums %}
    """
    unread_forums = []
    processed_forums = []

    # A user which is not authenticated will never see a forum as unread
    if not user.is_authenticated():
        return unread_forums

    # Forums are sorted by their position in the forums tree in order
    # to limit the number of operations required to determine the unread
    # forums below a forum which has the smallest position among the
    # forums from the initial set.
    # In fact, a forum is unread if at least one of its descendants
    # (including itself) is unread.
    # So the forums are sorted and then are processed by batches: from
    # a forum with a small level and all of its descendants, we get the
    # unread forums, and so on.
    sorted_forums = sorted(forums, key=lambda forum: forum.level)

    for forum in sorted_forums:
        if forum not in unread_forums and forum not in processed_forums:
            readable_forums = perm_handler.forum_list_filter(
                forum.get_descendants(include_self=True), user)
            unread = ForumReadTrack.objects.get_unread_forums_from_list(readable_forums, user)
            unread_forums.extend(unread)
            processed_forums.extend(readable_forums)

    return unread_forums
