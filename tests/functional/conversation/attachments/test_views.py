# -*- coding: utf-8 -*-

# Standard library imports
import os

# Third party imports
from django.conf import settings
from django.core.files import File
from django.db.models import get_model
from faker import Factory as FakerFactory
from guardian.shortcuts import assign_perm

# Local application / specific library imports
from machina.core.loading import get_class
from machina.test.factories import AttachmentFactory
from machina.test.factories import create_forum
from machina.test.factories import create_topic
from machina.test.factories import ForumReadTrackFactory
from machina.test.factories import PostFactory
from machina.test.testcases import BaseClientTestCase

faker = FakerFactory.create()

Attachment = get_model('attachments', 'Attachment')
ForumReadTrack = get_model('tracking', 'ForumReadTrack')
Post = get_model('conversation', 'Post')
Topic = get_model('conversation', 'Topic')
TopicReadTrack = get_model('tracking', 'TopicReadTrack')

PermissionHandler = get_class('permission.handler', 'PermissionHandler')


class TestTopicView(BaseClientTestCase):
    def setUp(self):
        super(TestTopicView, self).setUp()

        # Permission handler
        self.perm_handler = PermissionHandler()

        # Set up a top-level forum
        self.top_level_forum = create_forum()

        # Set up a topic and some posts
        self.topic = create_topic(forum=self.top_level_forum, poster=self.user)
        self.post = PostFactory.create(topic=self.topic, poster=self.user)

        # Set up an attachment
        f = open(settings.MEDIA_ROOT + '/attachment.jpg', 'rb')
        self.attachment_file = File(f)
        self.attachment = AttachmentFactory.create(
            post=self.post, file=self.attachment_file)

        # Mark the forum as read
        ForumReadTrackFactory.create(forum=self.top_level_forum, user=self.user)

        # Assign some permissions
        assign_perm('can_read_forum', self.user, self.top_level_forum)
        assign_perm('can_download_file', self.user, self.top_level_forum)

    def tearDown(self):
        self.attachment_file.close()
        attachments = Attachment.objects.all()
        for attachment in attachments:
            try:
                attachment.file.delete()
            except:
                pass

    def test_browsing_works(self):
        # Setup
        correct_url = self.attachment.get_absolute_url()
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        self.assertIsOk(response)

    def test_embed_the_correct_http_headers_in_the_response(self):
        # Setup
        correct_url = self.attachment.get_absolute_url()
        filename = os.path.basename(self.attachment.file.name)
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        self.assertIsOk(response)
        self.assertEqual(response['Content-Type'], 'image/jpeg')
        self.assertEqual(response['Content-Disposition'], 'attachment; filename={}'.format(filename))

    def test_is_able_to_handle_unknown_file_content_types(self):
        # Setup
        f = open(settings.MEDIA_ROOT + '/attachment.kyz', 'rb')
        attachment_file = File(f)
        attachment = AttachmentFactory.create(
            post=self.post, file=attachment_file)
        correct_url = attachment.get_absolute_url()
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        self.assertIsOk(response)
        self.assertEqual(response['Content-Type'], 'text/plain')
        attachment_file.close()
        attachment.file.delete()
