"""
    Forum signals
    =============

    This modules defines Django signals that can be triggered by the ``forum`` application.

"""

import django.dispatch


# Arguments:"previous_parent"
forum_moved = django.dispatch.Signal(providing_args=["previous_parent", ])
# Arguments:"forum", "user", "request", "response"
forum_viewed = django.dispatch.Signal(providing_args=["forum", "user", "request", "response", ])
