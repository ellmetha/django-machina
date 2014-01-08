# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
# Local application / specific library imports
from machina.apps.permission.abstract_models import AbstractForumGroupObjectPermission
from machina.apps.permission.abstract_models import AbstractForumUserObjectPermission


class ForumUserObjectPermission(AbstractForumUserObjectPermission):
    pass


class ForumGroupObjectPermission(AbstractForumGroupObjectPermission):
    pass
