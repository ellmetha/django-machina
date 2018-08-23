# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import template

from machina.conf.settings import get_user_display


register = template.Library()


@register.simple_tag
def get_username(user):
    return get_user_display()(user)
