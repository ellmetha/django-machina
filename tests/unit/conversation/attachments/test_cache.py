# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase

# Local application / specific library imports
from machina.conf import settings as machina_settings


class TestAttachmentCache(TestCase):
    def test_should_raise_at_import_if_the_cache_backend_is_not_configured(self):
        machina_settings.ATTACHMENT_CACHE_NAME = 'dummy'
        with self.assertRaises(ImproperlyConfigured):
            from machina.apps.conversation.attachments.cache import AttachmentCache
            AttachmentCache()
        machina_settings.ATTACHMENT_CACHE_NAME = 'machina_attachments'
