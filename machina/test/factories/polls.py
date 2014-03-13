# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.db.models import get_model
import factory

# Local application / specific library imports
from machina.test.factories import random_string
from machina.test.factories.auth import UserFactory
from machina.test.factories.conversation import TopicFactory

TopicPoll = get_model('polls', 'TopicPoll')
TopicPollOption = get_model('polls', 'TopicPollOption')
TopicPollVote = get_model('polls', 'TopicPollVote')


class TopicPollFactory(factory.DjangoModelFactory):
    FACTORY_FOR = TopicPoll
    topic = factory.SubFactory(TopicFactory)


class TopicPollOptionFactory(factory.DjangoModelFactory):
    FACTORY_FOR = TopicPollOption
    poll = factory.SubFactory(TopicPollFactory)
    text = subject = factory.LazyAttribute(lambda t: random_string(length=30))


class TopicPollVoteFactory(factory.DjangoModelFactory):
    FACTORY_FOR = TopicPollVote
    poll_option = factory.SubFactory(TopicPollOptionFactory)
    voter = factory.SubFactory(UserFactory)
