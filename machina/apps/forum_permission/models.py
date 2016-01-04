# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
# Local application / specific library imports
from machina.apps.forum_permission.abstract_models import AbstractForumPermission
from machina.apps.forum_permission.abstract_models import AbstractGroupForumPermission
from machina.apps.forum_permission.abstract_models import AbstractUserForumPermission
from machina.core.db.models import model_factory


ForumPermission = model_factory(AbstractForumPermission)
GroupForumPermission = model_factory(AbstractGroupForumPermission)
UserForumPermission = model_factory(AbstractUserForumPermission)
