import factory
import factory.django
from django.utils.text import slugify
from factory import fuzzy
from faker import Faker

from machina.core.db.models import get_model
from machina.test.factories.auth import UserFactory
from machina.test.factories.forum import ForumFactory


faker = Faker()

Post = get_model('forum_conversation', 'Post')
Topic = get_model('forum_conversation', 'Topic')


class TopicFactory(factory.django.DjangoModelFactory):
    forum = factory.SubFactory(ForumFactory)
    poster = factory.SubFactory(UserFactory)
    status = Topic.TOPIC_UNLOCKED
    subject = factory.LazyAttribute(lambda t: faker.text(max_nb_chars=200))
    slug = factory.LazyAttribute(lambda t: slugify(t.subject))

    class Meta:
        model = Topic


class PostFactory(factory.django.DjangoModelFactory):
    topic = factory.SubFactory(TopicFactory)
    poster = factory.SubFactory(UserFactory)
    subject = factory.LazyAttribute(lambda t: faker.text(max_nb_chars=200))
    content = fuzzy.FuzzyText(length=255)

    class Meta:
        model = Post


def build_topic(**attrs):
    """Create a new unlocked topic but do not save it."""
    params_dict = {'type': Topic.TOPIC_POST}
    params_dict.update(attrs)
    topic = TopicFactory.build(**params_dict)
    return topic


def create_topic(**attrs):
    """Save a new unlocked topic."""
    topic = build_topic(**attrs)
    topic.save()
    return topic
