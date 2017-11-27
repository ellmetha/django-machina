# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import inspect

from django import template

from machina.core.loading import get_class


PermissionHandler = get_class('forum_permission.handler', 'PermissionHandler')

register = template.Library()


@register.simple_tag(takes_context=True)
def get_permission(context, method, *args, **kwargs):
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
    return perm_method(*args, **kwargs)
