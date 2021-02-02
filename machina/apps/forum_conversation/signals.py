"""
    Forum conversation signals
    ==========================

    This modules defines Django signals that can be triggered by the ``forum`` application.

"""

import django.dispatch

# Arguments: "topic",  "user", "request", "response"
topic_viewed = django.dispatch.Signal()
