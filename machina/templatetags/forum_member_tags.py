from django import template

from machina.core.loading import get_class


get_forum_member_display_name = get_class('forum_member.shortcuts', 'get_forum_member_display_name')

register = template.Library()


@register.filter
def forum_member_display_name(user):
    """ Returns the forum member display name to use for a given user.

    Usage::

        {{ user|forum_member_display_name }}

    """
    return get_forum_member_display_name(user)
