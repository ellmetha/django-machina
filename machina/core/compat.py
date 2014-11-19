# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_lazy as _

# Local application / specific library imports

# PILImage
try:
    # Try from the Pillow (or one variant of PIL) install location first.
    from PIL import Image as PILImage
except ImportError as err:
    try:
        # If that failed, try the alternate import syntax for PIL.
        import Image as PILImage
    except ImportError as err:
        # Neither worked, so it's likely not installed.
        raise ImproperlyConfigured(
            _("Neither Pillow nor PIL could be imported: %s") % err
        )


# Django slugify
try:
    from django.utils.text import slugify
except ImportError:
    from django.template.defaultfilters import slugify


# force_bytes
try:
    from django.utils.encoding import force_bytes
except ImportError:
    from django.utils.encoding import smart_str as force_bytes


# A settings that can be used in foreign key declarations to ensure backwards compatibility
# with Django 1.4
AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')
