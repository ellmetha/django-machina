# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
# Local application / specific library imports


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
