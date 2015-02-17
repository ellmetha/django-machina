# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
# Local application / specific library imports
from machina.apps.member.abstract_models import AbstractProfile
from machina.core.db.models import model_factory


Profile = model_factory(AbstractProfile)
