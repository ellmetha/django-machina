# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
import factory
from faker import Factory as FakerFactory

# Local application / specific library imports

faker = FakerFactory.create()


class UserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = User
    username = factory.LazyAttribute(lambda t: faker.user_name())
    email = factory.Sequence(lambda n: 'test{0}@example.com'.format(n))
    password = '1234'
    is_active = True

    @classmethod
    def _prepare(cls, create, **kwargs):
        password = kwargs.pop('password', None)
        user = super(UserFactory, cls)._prepare(create, **kwargs)
        if password:
            user.set_password(password)
            if create:
                user.save()
        return user


class GroupFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Group
    name = factory.Sequence(lambda n: '{}-{}'.format(str(n), faker.job()))
