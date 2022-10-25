"""
    Forum signals
    =============

    This modules defines Django signals that can be triggered by the ``forum`` application.

"""

import django.dispatch


# Arguments:"previous_parent"
forum_moved = django.dispatch.Signal()
# Arguments:"forum", "user", "request", "response"
forum_viewed = django.dispatch.Signal()
