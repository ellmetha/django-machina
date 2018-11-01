"""
    Forum permission models
    =======================

    This module defines models provided by the ``forum_permission`` application.

"""

from machina.apps.forum_permission.abstract_models import (
    AbstractForumPermission, AbstractGroupForumPermission, AbstractUserForumPermission
)
from machina.core.db.models import model_factory


ForumPermission = model_factory(AbstractForumPermission)
GroupForumPermission = model_factory(AbstractGroupForumPermission)
UserForumPermission = model_factory(AbstractUserForumPermission)
