# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
# Local application / specific library imports
from machina.apps.forum_member.abstract_models import AbstractForumProfile
from machina.core.db.models import model_factory


ForumProfile = model_factory(AbstractForumProfile)
