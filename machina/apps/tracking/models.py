# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
import django

# Local application / specific library imports
from machina.apps.tracking.abstract_models import AbstractForumReadTrack
from machina.apps.tracking.abstract_models import AbstractTopicReadTrack
from machina.core.db.models import model_factory


ForumReadTrack = model_factory(AbstractForumReadTrack)
TopicReadTrack = model_factory(AbstractTopicReadTrack)


if django.VERSION < (1, 7):
    from .receivers import *  # noqa
