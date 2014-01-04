# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.db.models import get_model

# Local application / specific library imports
from machina.test.mixins import AdminBaseViewTestMixin
from machina.test.testcases import AdminClientTestCase
Post = get_model('conversation', 'Post')
Topic = get_model('conversation', 'Topic')


class TestPostAdmin(AdminClientTestCase, AdminBaseViewTestMixin):
    model = Post


class TestTopicAdmin(AdminClientTestCase, AdminBaseViewTestMixin):
    model = Topic
