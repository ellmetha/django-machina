# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
import factory

# Local application / specific library imports
from machina.core.db.models import get_model
from machina.test.factories.auth import UserFactory
from machina.test.factories.conversation import TopicFactory
from machina.test.factories.forum import ForumFactory

ForumReadTrack = get_model('tracking', 'ForumReadTrack')
TopicReadTrack = get_model('tracking', 'TopicReadTrack')


class ForumReadTrackFactory(factory.DjangoModelFactory):
    FACTORY_FOR = ForumReadTrack
    user = factory.SubFactory(UserFactory)
    forum = factory.SubFactory(ForumFactory)


class TopicReadTrackFactory(factory.DjangoModelFactory):
    FACTORY_FOR = TopicReadTrack
    user = factory.SubFactory(UserFactory)
    topic = factory.SubFactory(TopicFactory)
