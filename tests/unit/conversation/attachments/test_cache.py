# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase
from django.test.utils import override_settings

# Local application / specific library imports


class TestAttachmentCache(TestCase):
    @override_settings(CACHES={})
    def test_should_raise_at_import_if_the_cache_backend_is_not_configured(self):
        with self.assertRaises(ImproperlyConfigured):
            from machina.apps.conversation.attachments.cache import cache
            cache.get_backend()
