# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth.models import Group
from django.contrib.auth.models import User
import factory
from faker import Factory as FakerFactory

faker = FakerFactory.create()


class UserFactory(factory.DjangoModelFactory):
    username = factory.LazyAttribute(lambda t: faker.user_name())
    email = factory.Sequence(lambda n: 'test{0}@example.com'.format(n))
    password = '1234'
    is_active = True

    class Meta:
        model = User

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
    name = factory.Sequence(lambda n: '{}-{}'.format(str(n), faker.job()))

    class Meta:
        model = Group
