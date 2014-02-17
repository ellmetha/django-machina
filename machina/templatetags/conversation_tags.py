# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import unicode_literals

# Third party imports
from django import template

# Local application / specific library imports
from machina.core.loading import get_class

PermissionHandler = get_class('permission.handler', 'PermissionHandler')
perm_handler = PermissionHandler()

register = template.Library()


@register.filter
def posted_by(post, user):
    """
    This will return a boolean indicating if the passed user has posted
    the given forum post.

    Usage::

        {% if post|posted_by:user %}...{% endif %}
    """
    return post.poster == user


@register.filter
def can_be_edited_by(post, user):
    """
    Determines whether the given user can edit the considered post.

    Usage::

        {% if post|can_be_edited_by:user %}...{% endif %}
    """
    return perm_handler.can_edit_post(post, user)


@register.filter
def can_be_deleted_by(post, user):
    """
    Determines whether the given user can delete the considered post.

    Usage::

        {% if post|can_be_deleted_by:user %}...{% endif %}
    """
    return perm_handler.can_delete_post(post, user)
