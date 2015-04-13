# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.db.models import get_model

# Local application / specific library imports
from machina.test.mixins import AdminBaseViewTestMixin
from machina.test.testcases import AdminClientTestCase

Attachment = get_model('forum_attachments', 'Attachment')


class TestAttachmentAdmin(AdminClientTestCase, AdminBaseViewTestMixin):
    model = Attachment
