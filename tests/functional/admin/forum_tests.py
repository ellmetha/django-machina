# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.db.models import get_model

# Local application / specific library imports
from machina.test.mixins import AdminClientMixin
from machina.test.testcases import BaseClientTestCase
Forum = get_model('forum', 'Forum')


class TestForumAdmin(BaseClientTestCase, AdminClientMixin):
    model = Forum
