# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import unicode_literals
import inspect

# Third party imports
from django import template

# Local application / specific library imports
from machina.core.loading import get_class

PermissionHandler = get_class('forum_permission.handler', 'PermissionHandler')

register = template.Library()


@register.assignment_tag(takes_context=True)
def get_permission(context, method, user, **kwargs):
    """
    This will return a boolean indicating if the considered permission is
    granted for the passed user.

    Usage::

        {% get_permission 'can_access_moderation_panel' request.user as var %}
    """
    request = context.get('request', None)
    perm_handler = request.forum_permission_handler if request else PermissionHandler()

    allowed_methods = inspect.getmembers(perm_handler, predicate=inspect.ismethod)
    allowed_method_names = [a[0] for a in allowed_methods if not a[0].startswith('_')]

    if method not in allowed_method_names:
        raise template.TemplateSyntaxError(
            'Only the following methods are allowed through '
            'this templatetag: {}'.format(allowed_method_names))

    perm_method = getattr(perm_handler, method)

    a = lambda x: x * 2

    def raise_missing(arg):
        raise template.TemplateSyntaxError(
            'A `{}` keyword argument should be passed to this templatetag '
            'when requesting the `{}` method.'.format(arg, method))

    if method == 'can_download_files':
        post = kwargs.get('post', None)
        if post is None:
            raise_missing('post')
        return perm_method(post.topic.forum, user)
    elif method in ['can_edit_post', 'can_delete_post', ]:
        post = kwargs.get('post', None)
        if post is None:
            raise_missing('post')
        return perm_method(post, user)
    elif method == 'can_add_post':
        topic = kwargs.get('topic', None)
        if topic is None:
            raise_missing('topic')
        return perm_method(topic, user)
    elif method == 'can_vote_in_poll':
        poll = kwargs.get('poll', None)
        if poll is None:
            raise_missing('poll')
        return perm_method(poll, user)
    elif method in ['can_add_topic', 'can_move_topics']:
        forum = kwargs.get('forum', None)
        if forum is None:
            raise_missing('forum')
        return perm_method(forum, user)
    else:
        return perm_method(user)
