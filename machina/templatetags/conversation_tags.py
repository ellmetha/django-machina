# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import unicode_literals

# Third party imports
from django import template

# Local application / specific library imports
from machina.conf import settings as machina_settings
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


@register.filter
def can_be_enriched_by(topic, user):
    """
    This will return a boolean indicating if the considered user can append answers
    to the passed topic.

    Usage::

        {% if topic|can_be_enriched_by:user %}...{% endif %}
    """
    return perm_handler.can_add_post(topic, user)


@register.inclusion_tag('machina/conversation/topic_pages_inline_list.html')
def topic_pages_inline_list(topic):
    """
    This will render an inline pagination for the posts related to the
    given topic.

    Usage::

        {% topic_pages_inline_list my_topic %}
    """
    data_dict = {
        'topic': topic,
    }

    pages_number = (topic.posts_count // machina_settings.TOPIC_POSTS_NUMBER_PER_PAGE) + 1
    if pages_number > 5:
        data_dict['first_pages'] = range(1, 5)
        data_dict['last_page'] = pages_number
    elif pages_number > 1:
        data_dict['first_pages'] = range(1, pages_number + 1)

    return data_dict
