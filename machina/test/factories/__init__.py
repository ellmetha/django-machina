# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import unicode_literals
import random
import string

# Third party imports
# Local application / specific library imports


def random_string(length=10):
    return ''.join(random.choice(string.ascii_letters) for x in range(length))


from .auth import *
from .conversation import *
from .forum import *
