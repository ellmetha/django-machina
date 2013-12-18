# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.conf import settings

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

# Local application / specific library imports


# A settings that can be used in foreign key declarations to ensure backwards compatibility
# with Django 1.4
AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')
