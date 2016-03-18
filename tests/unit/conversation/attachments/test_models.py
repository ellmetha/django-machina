# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.encoding import force_bytes
import pytest

from machina.test.factories import AttachmentFactory
from machina.test.factories import create_forum
from machina.test.factories import create_topic
from machina.test.factories import PostFactory
from machina.test.factories import UserFactory


@pytest.mark.django_db
class TestAttachment(object):
    @pytest.fixture(autouse=True)
    def setup(self):
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
        assert attachment.filename == 'dummy_file.txt'
        attachment.file.delete()
