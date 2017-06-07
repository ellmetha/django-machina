# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import factory
from django.utils.text import slugify
from faker import Faker

from machina.core.db.models import get_model


faker = Faker()

Forum = get_model('forum', 'Forum')


class ForumFactory(factory.DjangoModelFactory):
    name = faker.text(max_nb_chars=100)
    slug = factory.LazyAttribute(lambda t: slugify(t.name))

    # Link forum specific
    link = faker.uri()

    class Meta:
        model = Forum


def build_forum(**attrs):
    """Create a new forum but do not save it."""
    params_dict = {'type': Forum.FORUM_POST}
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
    params_dict = {'type': Forum.FORUM_CAT}
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
    params_dict = {'type': Forum.FORUM_LINK}
    params_dict.update(attrs)
    link = ForumFactory.build(**params_dict)
    return link


def create_link_forum(**attrs):
    """Save a new link forum."""
    link = build_link_forum(**attrs)
    link.save()
    return link
