# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from machina.apps.forum_member.abstract_models import AbstractForumProfile
from machina.core.db.models import model_factory


ForumProfile = model_factory(AbstractForumProfile)
