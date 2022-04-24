import factory
import factory.django
from faker import Faker

from machina.core.db.models import get_model
from machina.test.factories.conversation import PostFactory


faker = Faker()

Attachment = get_model('forum_attachments', 'Attachment')


class AttachmentFactory(factory.django.DjangoModelFactory):
    post = factory.SubFactory(PostFactory)
    comment = faker.text(max_nb_chars=255)
    file = factory.django.FileField()

    class Meta:
        model = Attachment
