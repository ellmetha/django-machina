"""
    Forum member shortcuts
    ======================

    This module defines shortcut functions allowing to easily get forum member information.

"""


def get_forum_member_display_name(user):
    """ Given a specific user, returns their related display name. """
    return user.get_username()
