# -*- coding: utf-8 -*-

from machina.core.db.models import get_model
from machina.test.mixins import AdminBaseViewTestMixin
from machina.test.testcases import AdminClientTestCase

Attachment = get_model('forum_attachments', 'Attachment')


class TestAttachmentAdmin(AdminClientTestCase, AdminBaseViewTestMixin):
    model = Attachment
