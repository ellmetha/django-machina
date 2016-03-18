# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from machina.apps.forum_permission.abstract_models import AbstractForumPermission
from machina.apps.forum_permission.abstract_models import AbstractGroupForumPermission
from machina.apps.forum_permission.abstract_models import AbstractUserForumPermission
from machina.core.db.models import model_factory


ForumPermission = model_factory(AbstractForumPermission)
GroupForumPermission = model_factory(AbstractGroupForumPermission)
UserForumPermission = model_factory(AbstractUserForumPermission)
