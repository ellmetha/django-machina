# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.db.models import get_model
import factory
from factory import fuzzy

# Local application / specific library imports
from machina.test.factories import random_string
from machina.test.factories.auth import UserFactory
from machina.test.factories.forum import ForumFactory

Post = get_model('conversation', 'Post')
Topic = get_model('conversation', 'Topic')


class TopicFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Topic
    forum = factory.SubFactory(ForumFactory)
    poster = factory.SubFactory(UserFactory)
    subject = factory.LazyAttribute(lambda t: random_string(length=20))
    status = Topic.STATUS_CHOICES.topic_unlocked


class PostFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Post
    topic = factory.SubFactory(TopicFactory)
    poster = factory.SubFactory(UserFactory)
    content = fuzzy.FuzzyText(length=255)


def build_topic(**attrs):
    """Create a new unlocked topic but do not save it."""
    params_dict = {'type': Topic.TYPE_CHOICES.topic_post}
    params_dict.update(attrs)
    topic = TopicFactory.build(**params_dict)
    return topic


def create_topic(**attrs):
    """Save a new unlocked topic."""
    topic = build_topic(**attrs)
    topic.save()
    return topic
