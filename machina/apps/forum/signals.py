# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
import django.dispatch

# Local application / specific library imports


forum_moved = django.dispatch.Signal(providing_args=["previous_parent", ])
forum_viewed = django.dispatch.Signal(providing_args=["forum", "user", "request", "response", ])
