# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.utils.encoding import smart_text
from markdown2 import markdown as _markdown


def markdown(text, **kwargs):
    return smart_text(_markdown(text, **kwargs).strip())
