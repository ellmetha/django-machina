import factory
import factory.django
from django.utils.text import slugify
from faker import Faker

from machina.core.db.models import get_model


faker = Faker()

Forum = get_model('forum', 'Forum')
NAMES = [faker.name() for i in range(10)]


class ForumFactory(factory.django.DjangoModelFactory):
    name = factory.LazyAttribute(lambda obj: factory.fuzzy.FuzzyChoice(NAMES).fuzz())
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
