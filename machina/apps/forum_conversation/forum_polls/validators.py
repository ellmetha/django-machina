# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.core import validators

# Local application / specific library imports
from machina.conf import settings as machina_settings


poll_max_options = [
    validators.MinValueValidator(1),
    validators.MaxValueValidator(machina_settings.POLL_MAX_OPTIONS_PER_USER),
]
