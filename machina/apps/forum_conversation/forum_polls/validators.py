"""
    Forum polls validators
    ======================

    This module defines validators provided by the ``forum_polls`` application.

"""

from django.core import validators

from machina.conf import settings as machina_settings


poll_max_options = [
    validators.MinValueValidator(1),
    validators.MaxValueValidator(machina_settings.POLL_MAX_OPTIONS_PER_USER),
]
