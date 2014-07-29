# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
import django
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
if django.VERSION > (1, 4):
    from django.utils.text import slugify
else:
    from django.template.defaultfilters import slugify


# A settings that can be used in foreign key declarations to ensure backwards compatibility
# with Django 1.4
AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


# Django 1.7 and greater come with a built-in migration system that should be used prior to South.
# To support South migrations with older versions of Django, developers should configure their
# SOUTH_MIGRATION_MODULES setting.
SOUTH_ERROR_MESSAGE = """\n
To support South migrations, you should customize the SOUTH_MIGRATION_MODULES setting as follow:

from machina.core.compat import MACHINA_SOUTH_MIGRATION_MODULES
SOUTH_MIGRATION_MODULES = dict(SOUTH_MIGRATION_MODULES.items() + MACHINA_SOUTH_MIGRATION_MODULES.items())
"""

MACHINA_SOUTH_MIGRATION_MODULES = {
    'conversation': 'machina.apps.conversation.south_migrations',
    'polls': 'machina.apps.conversation.polls.south_migrations',
    'forum': 'machina.apps.forum.south_migrations',
    'member': 'machina.apps.member.south_migrations',
    'permission': 'machina.apps.permission.south_migrations',
    'tracking': 'machina.apps.tracking.south_migrations',
}
