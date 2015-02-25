# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
import factory
from faker import Factory as FakerFactory

# Local application / specific library imports
from machina.core.db.models import get_model
from machina.test.factories.auth import UserFactory
from machina.test.factories.conversation import TopicFactory

faker = FakerFactory.create()

TopicPoll = get_model('forum_polls', 'TopicPoll')
TopicPollOption = get_model('forum_polls', 'TopicPollOption')
TopicPollVote = get_model('forum_polls', 'TopicPollVote')


class TopicPollFactory(factory.DjangoModelFactory):
    FACTORY_FOR = TopicPoll
    topic = factory.SubFactory(TopicFactory)
    question = faker.text(max_nb_chars=200)


class TopicPollOptionFactory(factory.DjangoModelFactory):
    FACTORY_FOR = TopicPollOption
    poll = factory.SubFactory(TopicPollFactory)
    text = faker.text(max_nb_chars=100)


class TopicPollVoteFactory(factory.DjangoModelFactory):
    FACTORY_FOR = TopicPollVote
    poll_option = factory.SubFactory(TopicPollOptionFactory)
    voter = factory.SubFactory(UserFactory)
