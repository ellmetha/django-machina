# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django import template

# Local application / specific library imports
from machina.conf import settings as machina_settings

register = template.Library()


@register.filter
def is_anonymous(user):
    """
    Determines whether the given user is the anonymous user.

    Usage::

        {% if topic.poster|is_anonymous %}...{% endif %}
    """
    return user.id == machina_settings.ANONYMOUS_USER_ID \
        or not user.is_authenticated()
