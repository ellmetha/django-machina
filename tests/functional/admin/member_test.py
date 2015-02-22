# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.db.models import get_model

# Local application / specific library imports
from machina.test.mixins import AdminBaseViewTestMixin
from machina.test.testcases import AdminClientTestCase

Profile = get_model('forum_member', 'Profile')


class TestProfileAdmin(AdminClientTestCase, AdminBaseViewTestMixin):
    model = Profile
