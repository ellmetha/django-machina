# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from machina.apps.forum_conversation.forum_polls.abstract_models import AbstractTopicPoll
from machina.apps.forum_conversation.forum_polls.abstract_models import AbstractTopicPollOption
from machina.apps.forum_conversation.forum_polls.abstract_models import AbstractTopicPollVote


class TopicPoll(AbstractTopicPoll):
    pass


class TopicPollOption(AbstractTopicPollOption):
    pass


class TopicPollVote(AbstractTopicPollVote):
    pass
