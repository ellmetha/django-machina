# -*- coding: utf-8 -*-

from django import template
from django.template.defaultfilters import stringfilter

from machina.models.fields import render_func


register = template.Library()


@register.filter(is_safe=True)
@stringfilter
def rendered(value):
    return render_func(value)
