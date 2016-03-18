# -*- coding: utf-8 -*-

from __future__ import unicode_literals


def get_client_ip(request):
    """
    Given an HTTP request, returns the related IP address.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', None)
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
