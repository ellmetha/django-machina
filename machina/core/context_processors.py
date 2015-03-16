# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
# Local application / specific library imports
from machina.conf import settings as machina_settings


def metadata(request):
    """
    Append some Machina-specific data to the template context.
    """
    return {
        'MACHINA_FORUM_NAME': machina_settings.MACHINA_FORUM_NAME,
    }
