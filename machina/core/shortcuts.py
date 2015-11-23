# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import unicode_literals

# Third party imports
from django.shortcuts import _get_queryset

# Local application / specific library imports


def get_object_or_none(klass, *args, **kwargs):
    """
    Calls get() on a given model manager, but it returns None instead of the model’s DoesNotExist exception.
    """
    queryset = _get_queryset(klass)
    try:
        return queryset.get(*args, **kwargs)
    except:
        return None


def refresh(instance):
    """
    Select and return instance from database.
    Usage: instance = refresh(instance)
    """
    return instance.__class__.objects.get(pk=instance.pk)
