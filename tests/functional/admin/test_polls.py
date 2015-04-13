# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.db.models import get_model

# Local application / specific library imports
from machina.test.mixins import AdminBaseViewTestMixin
from machina.test.testcases import AdminClientTestCase

TopicPoll = get_model('forum_polls', 'TopicPoll')
TopicPollOption = get_model('forum_polls', 'TopicPollOption')
TopicPollVote = get_model('forum_polls', 'TopicPollVote')


class TestTopicPollAdmin(AdminClientTestCase, AdminBaseViewTestMixin):
    model = TopicPoll


class TestTopicPollOptionAdmin(AdminClientTestCase, AdminBaseViewTestMixin):
    model = TopicPollOption


class TestTopicPollVoteAdmin(AdminClientTestCase, AdminBaseViewTestMixin):
    model = TopicPollVote
