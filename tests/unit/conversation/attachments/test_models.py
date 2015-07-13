# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.core.files.uploadedfile import SimpleUploadedFile

# Local application / specific library imports
from machina.core.compat import force_bytes
from machina.test.factories import AttachmentFactory
from machina.test.factories import create_forum
from machina.test.factories import create_topic
from machina.test.factories import PostFactory
from machina.test.factories import UserFactory
from machina.test.testcases import BaseUnitTestCase


class TestAttachment(BaseUnitTestCase):
    def setUp(self):
        self.u1 = UserFactory.create()

        # Set up a top-level forum, an associated topic and a post
        self.top_level_forum = create_forum()
        self.topic = create_topic(forum=self.top_level_forum, poster=self.u1)
        self.post = PostFactory.create(topic=self.topic, poster=self.u1)

    def test_objects_know_their_filenames(self):
        # Setup
        f = SimpleUploadedFile('dummy_file.txt', force_bytes('file_content'))
        attachment = AttachmentFactory.create(post=self.post, file=f)
        # Run & check
        self.assertEqual(attachment.filename, 'dummy_file.txt')
        attachment.file.delete()
