# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django import template
from django.template.defaultfilters import stringfilter

# Local application / specific library imports
from machina.models.fields import render_func

register = template.Library()


@register.filter(is_safe=True)
@stringfilter
def rendered(value):
    return render_func(value)
