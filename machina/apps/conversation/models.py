# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
# Local application / specific library imports
from machina.apps.conversation.abstract_models import AbstractPost
from machina.apps.conversation.abstract_models import AbstractTopic
from machina.apps.conversation.abstract_models import AbstractTopicReadTrack


class Topic(AbstractTopic):
    pass


class Post(AbstractPost):
    pass


class TopicReadTrack(AbstractTopicReadTrack):
    pass
