# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from machina.apps.forum_conversation.abstract_models import AbstractPost
from machina.apps.forum_conversation.abstract_models import AbstractTopic
from machina.core.db.models import model_factory


Topic = model_factory(AbstractTopic)
Post = model_factory(AbstractPost)
