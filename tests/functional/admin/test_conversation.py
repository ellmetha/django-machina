# -*- coding: utf-8 -*-

from machina.core.db.models import get_model
from machina.test.mixins import AdminBaseViewTestMixin
from machina.test.testcases import AdminClientTestCase
Post = get_model('forum_conversation', 'Post')
Topic = get_model('forum_conversation', 'Topic')


class TestPostAdmin(AdminClientTestCase, AdminBaseViewTestMixin):
    model = Post


class TestTopicAdmin(AdminClientTestCase, AdminBaseViewTestMixin):
    model = Topic
