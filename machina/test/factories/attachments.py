# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
import factory
from faker import Factory as FakerFactory

# Local application / specific library imports
from machina.core.db.models import get_model
from machina.test.factories.conversation import PostFactory

faker = FakerFactory.create()

Attachment = get_model('forum_attachments', 'Attachment')


class AttachmentFactory(factory.DjangoModelFactory):
    post = factory.SubFactory(PostFactory)
    comment = faker.text(max_nb_chars=255)

    class Meta:
        model = Attachment
