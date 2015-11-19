# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import unicode_literals

# Third party imports
from django import VERSION as DJANGO_VERSION
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_lazy as _

# Local application / specific library imports

# PILImage
try:
    # Try from the Pillow (or one variant of PIL) install location first.
    from PIL import Image as PILImage
except ImportError as err:
    try:
        # If that failed, try the alternate import syntax for PIL.
        import Image as PILImage  # noqa
    except ImportError as err:
        # Neither worked, so it's likely not installed.
        raise ImproperlyConfigured(
            _('Neither Pillow nor PIL could be imported: {}').format(err)
        )


# get_cache
if DJANGO_VERSION >= (1, 7):
    from django.core.cache import caches

    def get_cache(key):
        return caches[key]
else:
    from django.core.cache import get_cache  # noqa


# URL patterns
if DJANGO_VERSION >= (1, 8):
    patterns = lambda urls: urls
else:
    from django.conf.urls import patterns as urlpatterns
    patterns = lambda urls: urlpatterns('', *urls)
