# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import unicode_literals

# Third party imports
from django import template

# Local application / specific library imports
from machina.core.loading import get_class

TrackingHandler = get_class('forum_tracking.handler', 'TrackingHandler')
tracks_handler = TrackingHandler()

register = template.Library()


@register.assignment_tag
def get_unread_forums(forums, user):
    """
    This will return a list of unread forums for the given user from a given set of forums.

    Usage::

        {% get_unread_forums forums request.user as unread_forums %}
    """
    return tracks_handler.get_unread_forums(forums, user)


@register.assignment_tag
def get_unread_topics(topics, user):
    """
    This will return a list of unread topics for the given user from a given set of forums.

    Usage::

        {% get_unread_topics topics request.user as unread_topics %}
    """
    return tracks_handler.get_unread_topics(topics, user)
