# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import unicode_literals

# Third party imports
from django.core import validators

# Local application / specific library imports


validate_poll_max_options = validators.MinValueValidator(1)
