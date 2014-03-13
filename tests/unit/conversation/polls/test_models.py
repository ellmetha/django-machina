# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.core.exceptions import ValidationError
from django.test import TestCase

# Local application / specific library imports
from machina.test.factories import create_forum
from machina.test.factories import create_topic
from machina.test.factories import PostFactory
from machina.test.factories import TopicPollFactory
from machina.test.factories import UserFactory


class TestTopicPoll(TestCase):
    def setUp(self):
        self.u1 = UserFactory.create()

        # Set up a top-level forum, an associated topic and a post
        self.top_level_forum = create_forum()
        self.topic = create_topic(forum=self.top_level_forum, poster=self.u1)
        self.post = PostFactory.create(topic=self.topic, poster=self.u1)

    def test_cannot_save_a_poll_for_which_the_users_cannot_choose_any_option(self):
        # Run & Check
        with self.assertRaises(ValidationError):
            poll = TopicPollFactory.build(topic=self.topic, max_options=0)
            poll.full_clean()
