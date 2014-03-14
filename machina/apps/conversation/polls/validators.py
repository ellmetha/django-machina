# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.core import validators

# Local application / specific library imports


validate_poll_max_options = validators.MinValueValidator(1)
