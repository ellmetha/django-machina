# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core import validators

from machina.conf import settings as machina_settings


poll_max_options = [
    validators.MinValueValidator(1),
    validators.MaxValueValidator(machina_settings.POLL_MAX_OPTIONS_PER_USER),
]
