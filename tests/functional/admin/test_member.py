# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
# Local application / specific library imports
from machina.core.db.models import get_model
from machina.test.mixins import AdminBaseViewTestMixin
from machina.test.testcases import AdminClientTestCase

ForumProfile = get_model('forum_member', 'ForumProfile')


class TestForumProfileAdmin(AdminClientTestCase, AdminBaseViewTestMixin):
    model = ForumProfile
