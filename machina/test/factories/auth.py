import factory
import factory.django
from django.contrib.auth.models import Group, User
from faker import Faker


faker = Faker()


class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Sequence(lambda n: '{}-{}'.format(faker.user_name(), n))
    email = factory.Sequence(lambda n: 'test{0}@example.com'.format(n))
    password = '1234'
    is_active = True

    class Meta:
        model = User

    @classmethod
    def _prepare(cls, create, **kwargs):
        password = kwargs.pop('password', None)
        user = super()._prepare(create, **kwargs)
        if password:
            user.set_password(password)
            if create:
                user.save()
        return user


class GroupFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: '{}-{}'.format(str(n), faker.job()))

    class Meta:
        model = Group
