# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from machina.apps.forum.abstract_models import AbstractForum
from machina.core.db.models import model_factory


Forum = model_factory(AbstractForum)
