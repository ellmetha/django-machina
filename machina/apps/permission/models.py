# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
# Local application / specific library imports
from machina.apps.permission.abstract_models import AbstractForumGroupObjectPermission
from machina.apps.permission.abstract_models import AbstractForumUserObjectPermission
from machina.core.db.models import model_factory


ForumUserObjectPermission = model_factory(AbstractForumUserObjectPermission)
ForumGroupObjectPermission = model_factory(AbstractForumGroupObjectPermission)
