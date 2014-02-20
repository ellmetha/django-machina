# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
# Local application / specific library imports
from machina.apps.tracking.abstract_models import AbstractForumReadTrack
from machina.apps.tracking.abstract_models import AbstractTopicReadTrack


class ForumReadTrack(AbstractForumReadTrack):
    pass


class TopicReadTrack(AbstractTopicReadTrack):
    pass


from .receivers import *
