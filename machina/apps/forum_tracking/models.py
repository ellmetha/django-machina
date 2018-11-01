"""
    Forum tracking models
    =====================

    This module defines models provided by the ``forum_tracking`` application.

"""

from machina.apps.forum_tracking.abstract_models import (
    AbstractForumReadTrack, AbstractTopicReadTrack
)
from machina.core.db.models import model_factory


ForumReadTrack = model_factory(AbstractForumReadTrack)
TopicReadTrack = model_factory(AbstractTopicReadTrack)
