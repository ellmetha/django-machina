from django import template

from machina.core.loading import get_class


TrackingHandler = get_class('forum_tracking.handler', 'TrackingHandler')

register = template.Library()


@register.simple_tag(takes_context=True)
def get_unread_topics(context, topics, user):
    """ This will return a list of unread topics for the given user from a given set of topics.

    Usage::

        {% get_unread_topics topics request.user as unread_topics %}

    """
    request = context.get('request', None)
    return TrackingHandler(request=request).get_unread_topics(topics, user)
