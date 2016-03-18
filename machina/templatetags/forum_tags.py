# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import template

from machina.core.db.models import get_model
from machina.core.loading import get_class

Forum = get_model('forum', 'Forum')

PermissionHandler = get_class('forum_permission.handler', 'PermissionHandler')

register = template.Library()


@register.assignment_tag(takes_context=True)
def get_forum_last_post(context, forum, user):
    """
    This will return the last post that can be read by the passed user (permissions check).

    Usage::

        {% get_forum_last_post forum request.user as var %}
    """
    request = context.get('request', None)
    perm_handler = request.forum_permission_handler if request else PermissionHandler()

    # Retrieve the last post link associated with the current forum
    last_post = perm_handler.get_forum_last_post(forum, user)
    return last_post


@register.inclusion_tag('forum/forum_list.html', takes_context=True)
def forum_list(context, forums):
    """
    This will render the given list of forums by respecting the order and the depth of each
    forum in the forums tree.

    Usage::

        {% forum_list my_forums %}
    """
    request = context.get('request', None)
    data_dict = {
        'forums': forums,
        'user': request.user,
        'request': request,
    }

    forums_copy = sorted(forums, key=lambda forum: forum.level)
    if forums_copy:
        root_level = forums_copy[0].level
        data_dict['root_level'] = root_level
        data_dict['root_level_middle'] = root_level + 1
        data_dict['root_level_sub'] = root_level + 2

    return data_dict
