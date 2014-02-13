# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
import django.dispatch

# Local application / specific library imports


topic_viewed = django.dispatch.Signal(providing_args=["topic", "user", "request", "response", ])
