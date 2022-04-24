import factory
import factory.django
from faker import Faker

from machina.core.db.models import get_model
from machina.test.factories.auth import UserFactory
from machina.test.factories.conversation import TopicFactory


faker = Faker()

TopicPoll = get_model('forum_polls', 'TopicPoll')
TopicPollOption = get_model('forum_polls', 'TopicPollOption')
TopicPollVote = get_model('forum_polls', 'TopicPollVote')


class TopicPollFactory(factory.django.DjangoModelFactory):
    topic = factory.SubFactory(TopicFactory)
    question = faker.text(max_nb_chars=200)

    class Meta:
        model = TopicPoll


class TopicPollOptionFactory(factory.django.DjangoModelFactory):
    poll = factory.SubFactory(TopicPollFactory)
    text = faker.text(max_nb_chars=100)

    class Meta:
        model = TopicPollOption


class TopicPollVoteFactory(factory.django.DjangoModelFactory):
    poll_option = factory.SubFactory(TopicPollOptionFactory)
    voter = factory.SubFactory(UserFactory)

    class Meta:
        model = TopicPollVote
