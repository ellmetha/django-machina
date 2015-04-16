# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import unicode_literals

# Third party imports
import factory
from faker import Factory as FakerFactory

# Local application / specific library imports
from machina.core.db.models import get_model

faker = FakerFactory.create()

ForumPermission = get_model('forum_permission', 'ForumPermission')
UserForumPermission = get_model('forum_permission', 'UserForumPermission')


class ForumPermissionFactory(factory.DjangoModelFactory):
    codename = factory.Sequence(lambda n: 'perm-{}'.format(n))
    name = faker.text(max_nb_chars=150)

    class Meta:
        model = ForumPermission


class UserForumPermissionFactory(factory.DjangoModelFactory):
    permission = factory.SubFactory(ForumPermissionFactory)

    class Meta:
        model = UserForumPermission
