# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import unicode_literals

# Third party imports
from django.core.exceptions import ImproperlyConfigured
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

# Local application / specific library imports
from machina.apps.conversation.attachments.cache import cache
from machina.conf import settings as machina_settings
from machina.core.compat import force_bytes


class TestAttachmentCache(TestCase):
    def test_should_raise_at_import_if_the_cache_backend_is_not_configured(self):
        # Run & check
        machina_settings.ATTACHMENT_CACHE_NAME = 'dummy'
        with self.assertRaises(ImproperlyConfigured):
            from machina.apps.conversation.attachments.cache import AttachmentCache
            AttachmentCache()
        machina_settings.ATTACHMENT_CACHE_NAME = 'machina_attachments'

    def test_is_able_to_store_the_state_of_request_files(self):
        # Setup
        f1 = SimpleUploadedFile('file1.txt', force_bytes('file_content_1'))
        f2 = SimpleUploadedFile('file2.txt', force_bytes('file_content_2_long'))
        f2.charset = 'iso-8859-1'
        files = {'f1': f1, 'f2': f2}
        real_cache = cache.get_backend()
        # Run
        cache.set('mykey', files)
        states = real_cache.get('mykey')
        # Check
        self.assertEqual(states['f1']['name'], 'file1.txt')
        self.assertEqual(states['f1']['content'], force_bytes('file_content_1'))
        self.assertIsNone(states['f1']['charset'])
        self.assertEqual(states['f1']['content_type'], 'text/plain')
        self.assertEqual(states['f1']['size'], 14)
        self.assertEqual(states['f2']['name'], 'file2.txt')
        self.assertEqual(states['f2']['content'], force_bytes('file_content_2_long'))
        self.assertEqual(states['f2']['charset'], 'iso-8859-1')
        self.assertEqual(states['f2']['content_type'], 'text/plain')
        self.assertEqual(states['f2']['size'], 19)
