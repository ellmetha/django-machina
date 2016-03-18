# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import factory
from faker import Factory as FakerFactory

from machina.core.db.models import get_model
from machina.test.factories.conversation import PostFactory

faker = FakerFactory.create()

Attachment = get_model('forum_attachments', 'Attachment')


class AttachmentFactory(factory.DjangoModelFactory):
    post = factory.SubFactory(PostFactory)
    comment = faker.text(max_nb_chars=255)

    class Meta:
        model = Attachment
