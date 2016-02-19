# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_lazy as _


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
