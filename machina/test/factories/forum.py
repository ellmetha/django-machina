# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.db.models import get_model
import factory

# Local application / specific library imports
from machina.test.factories import random_string

Forum = get_model('forum', 'Forum')


class ForumFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Forum
    name = factory.LazyAttribute(lambda t: random_string(length=15))

    # Link forum specific
    link = factory.LazyAttribute(lambda obj: 'http://www.goto{}.com'.format(obj.name))


def build_forum(**attrs):
    """Create a new forum but do not save it."""
    params_dict = {'type': Forum.TYPE_CHOICES.forum_post}
    params_dict.update(attrs)
    forum = ForumFactory.build(**params_dict)
    return forum


def create_forum(**attrs):
    """Save a new forum."""
    forum = build_forum(**attrs)
    forum.save()
    return forum


def build_category_forum(**attrs):
    """Create a new category forum but do not save it."""
    params_dict = {'type': Forum.TYPE_CHOICES.forum_cat}
    params_dict.update(attrs)
    category = ForumFactory.build(**params_dict)
    return category


def create_category_forum(**attrs):
    """Save a new category forum."""
    category = build_category_forum(**attrs)
    category.save()
    return category


def build_link_forum(**attrs):
    """Create a new link forum but do not save it."""
    params_dict = {'type': Forum.TYPE_CHOICES.forum_link}
    params_dict.update(attrs)
    link = ForumFactory.build(**params_dict)
    return link


def create_link_forum(**attrs):
    """Save a new link forum."""
    link = build_link_forum(**attrs)
    link.save()
    return link
