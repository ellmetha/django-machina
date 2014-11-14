# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.db.models import get_model
import factory
from faker import Factory as FakerFactory

# Local application / specific library imports
from machina.test.factories.conversation import PostFactory

faker = FakerFactory.create()

Attachment = get_model('attachments', 'Attachment')


class AttachmentFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Attachment
    post = factory.SubFactory(PostFactory)
    comment = factory.LazyAttribute(lambda t: faker.text(max_nb_chars=255))
