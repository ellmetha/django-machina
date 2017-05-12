# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import template

from machina.core.loading import get_class

TrackingHandler = get_class('forum_tracking.handler', 'TrackingHandler')

register = template.Library()


@register.assignment_tag(takes_context=True)
def get_unread_forums(context, user):
    """
    This will return the list of unread forums for the given user.

    Usage::

        {% get_unread_forums request.user as unread_forums %}
    """
    request = context.get('request', None)
    return TrackingHandler(request=request).get_unread_forums(user)


@register.assignment_tag(takes_context=True)
def get_unread_topics(context, topics, user):
    """
    This will return a list of unread topics for the given user from a given set of topics.

    Usage::

        {% get_unread_topics topics request.user as unread_topics %}
    """
    request = context.get('request', None)
    return TrackingHandler(request=request).get_unread_topics(topics, user)


@register.assignment_tag(takes_context=True)
def get_oldest_unread_post(context, topic, user):
    """
    This will return the oldest unread post for the given user from a given topic.

    Usage::

        {% get_oldest_unread_post topic request.user as oldest_unread_post %}
    """
    request = context.get('request', None)
    return TrackingHandler(request=request).get_oldest_unread_post(topic, user)
