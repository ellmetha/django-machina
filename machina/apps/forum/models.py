# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
# Local application / specific library imports
from machina.apps.forum.abstract_models import AbstractForum


class Forum(AbstractForum):
    pass


from .receivers import *
