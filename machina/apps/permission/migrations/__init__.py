# -*- coding: utf-8 -*-
# Standard library imports
# Third party imports
# Local application / specific library imports


# These migrations will work if Django 1.7 or greater is installed
try:
    from django.db import migrations
except ImportError:
    from django.core.exceptions import ImproperlyConfigured
    from machina.core.compat import SOUTH_ERROR_MESSAGE
    raise ImproperlyConfigured(SOUTH_ERROR_MESSAGE)
