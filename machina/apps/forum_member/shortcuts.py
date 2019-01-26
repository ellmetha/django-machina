"""
    Forum member shortcuts
    ======================

    This module defines shortcut functions allowing to easily get forum member information.

"""

from machina.conf import settings as machina_settings


def get_forum_member_display_name(user):
    """ Given a specific user, returns their related display name. """
    return getattr(user, machina_settings.USER_DISPLAY_NAME_METHOD)()
