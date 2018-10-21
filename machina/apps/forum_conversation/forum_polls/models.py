"""
    Forum polls models
    ==================

    This module defines models provided by the ``forum_polls`` application.

"""

from machina.apps.forum_conversation.forum_polls.abstract_models import AbstractTopicPoll
from machina.apps.forum_conversation.forum_polls.abstract_models import AbstractTopicPollOption
from machina.apps.forum_conversation.forum_polls.abstract_models import AbstractTopicPollVote
from machina.core.db.models import model_factory


TopicPoll = model_factory(AbstractTopicPoll)
TopicPollOption = model_factory(AbstractTopicPollOption)
TopicPollVote = model_factory(AbstractTopicPollVote)
