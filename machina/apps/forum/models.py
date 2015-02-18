# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
import django

# Local application / specific library imports
from machina.apps.forum.abstract_models import AbstractForum
from machina.core.db.models import model_factory


Forum = model_factory(AbstractForum)


if django.VERSION < (1, 7):  # pragma: no cover
    from .receivers import *  # noqa
