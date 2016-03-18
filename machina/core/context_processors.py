# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from machina.conf import settings as machina_settings


def metadata(request):
    """
    Append some Machina-specific data to the template context.
    """
    return {
        'MACHINA_FORUM_NAME': machina_settings.MACHINA_FORUM_NAME,
    }
