# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
# Local application / specific library imports
from machina.apps.forum.abstract_models import AbstractForum
from machina.core.db.models import model_factory


Forum = model_factory(AbstractForum)
