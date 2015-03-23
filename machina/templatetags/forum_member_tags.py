# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django import template
from django.conf import settings

# Local application / specific library imports

register = template.Library()


@register.filter
def is_anonymous(user):
    """
    Determines whether the given user is the anonymous user.

    Usage::

        {% if topic.poster|is_anonymous %}...{% endif %}
    """
    return (user.id == settings.ANONYMOUS_USER_ID if hasattr(settings, 'ANONYMOUS_USER_ID') else False) \
        or not user.is_authenticated()
