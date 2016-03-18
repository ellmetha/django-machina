# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import django.dispatch


topic_viewed = django.dispatch.Signal(providing_args=["topic", "user", "request", "response", ])
