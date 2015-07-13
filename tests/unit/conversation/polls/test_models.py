# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.core.exceptions import ValidationError

# Local application / specific library imports
from machina.test.factories import create_forum
from machina.test.factories import create_topic
from machina.test.factories import PostFactory
from machina.test.factories import TopicPollFactory
from machina.test.factories import TopicPollOptionFactory
from machina.test.factories import TopicPollVoteFactory
from machina.test.factories import UserFactory
from machina.test.testcases import BaseUnitTestCase


class TestTopicPoll(BaseUnitTestCase):
    def setUp(self):
        self.u1 = UserFactory.create()

        # Set up a top-level forum, an associated topic and a post
        self.top_level_forum = create_forum()
        self.topic = create_topic(forum=self.top_level_forum, poster=self.u1)
        self.post = PostFactory.create(topic=self.topic, poster=self.u1)

    def test_cannot_save_a_poll_for_which_the_users_cannot_choose_any_option(self):
        # Run & Check
        with self.assertRaises(ValidationError):
            poll = TopicPollFactory.build(topic=self.topic, max_options=0)
            poll.full_clean()

    def test_cannot_save_a_poll_for_which_the_users_can_choose_too_many_options(self):
        # Run & Check
        with self.assertRaises(ValidationError):
            poll = TopicPollFactory.build(topic=self.topic, max_options=50)
            poll.full_clean()

    def test_can_return_a_list_of_all_related_votes(self):
        # Setup
        u2 = UserFactory.create()
        poll = TopicPollFactory.create(topic=self.topic, max_options=2)
        option_1 = TopicPollOptionFactory.create(poll=poll)
        option_2 = TopicPollOptionFactory.create(poll=poll)
        # Run
        vote_1 = TopicPollVoteFactory.create(poll_option=option_1, voter=self.u1)
        vote_2 = TopicPollVoteFactory.create(poll_option=option_2, voter=self.u1)
        vote_3 = TopicPollVoteFactory.create(poll_option=option_2, voter=u2)
        # Check
        self.assertQuerysetEqual(poll.votes, [vote_1, vote_2, vote_3])


class TestTopicPollOption(BaseUnitTestCase):
    def setUp(self):
        self.u1 = UserFactory.create()

        # Set up a top-level forum, an associated topic and a post
        self.top_level_forum = create_forum()
        self.topic = create_topic(forum=self.top_level_forum, poster=self.u1)
        self.post = PostFactory.create(topic=self.topic, poster=self.u1)

    def test_knows_its_percentage(self):
        # Setup
        u2 = UserFactory.create()
        poll = TopicPollFactory.create(topic=self.topic, max_options=2)
        option_1 = TopicPollOptionFactory.create(poll=poll)
        option_2 = TopicPollOptionFactory.create(poll=poll)
        TopicPollVoteFactory.create(poll_option=option_1, voter=self.u1)
        TopicPollVoteFactory.create(poll_option=option_2, voter=self.u1)
        TopicPollVoteFactory.create(poll_option=option_1, voter=u2)
        TopicPollVoteFactory.create(poll_option=option_2, voter=u2)
        # Run & check
        self.assertEqual(option_1.percentage, 50)
        self.assertEqual(option_2.percentage, 50)
