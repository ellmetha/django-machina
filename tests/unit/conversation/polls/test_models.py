# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.exceptions import ValidationError
import pytest

from machina.test.factories import create_forum
from machina.test.factories import create_topic
from machina.test.factories import PostFactory
from machina.test.factories import TopicPollFactory
from machina.test.factories import TopicPollOptionFactory
from machina.test.factories import TopicPollVoteFactory
from machina.test.factories import UserFactory


@pytest.mark.django_db
class TestTopicPoll(object):
    @pytest.fixture(autouse=True)
    def setup(self):
        self.u1 = UserFactory.create()

        # Set up a top-level forum, an associated topic and a post
        self.top_level_forum = create_forum()
        self.topic = create_topic(forum=self.top_level_forum, poster=self.u1)
        self.post = PostFactory.create(topic=self.topic, poster=self.u1)

    def test_cannot_save_a_poll_for_which_the_users_cannot_choose_any_option(self):
        # Run & Check
        with pytest.raises(ValidationError):
            poll = TopicPollFactory.build(topic=self.topic, max_options=0)
            poll.full_clean()

    def test_cannot_save_a_poll_for_which_the_users_can_choose_too_many_options(self):
        # Run & Check
        with pytest.raises(ValidationError):
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
        assert set(poll.votes) == set([vote_1, vote_2, vote_3])


@pytest.mark.django_db
class TestTopicPollOption(object):
    @pytest.fixture(autouse=True)
    def setup(self):
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
        assert option_1.percentage == 50
        assert option_2.percentage == 50


@pytest.mark.django_db
class TestTopicPollVote(object):
    @pytest.fixture(autouse=True)
    def setup(self):
        self.u1 = UserFactory.create()

        # Set up a top-level forum, an associated topic and a post
        self.top_level_forum = create_forum()
        self.topic = create_topic(forum=self.top_level_forum, poster=self.u1)
        self.post = PostFactory.create(topic=self.topic, poster=self.u1)

    def test_must_be_associated_with_a_user_or_a_session_key_to_be_created(self):
        # Setup
        poll = TopicPollFactory.create(topic=self.topic, max_options=2)
        option_1 = TopicPollOptionFactory.create(poll=poll)
        TopicPollOptionFactory.create(poll=poll)

        # Run & check
        with pytest.raises(ValidationError):
            vote = TopicPollVoteFactory.build(
                poll_option=option_1, voter=None, anonymous_key=None)
            vote.clean()

    def test_cannot_be_associated_with_a_user_and_a_session_key_at_the_same_time_to_be_created(self):  # noqa
        # Setup
        poll = TopicPollFactory.create(topic=self.topic, max_options=2)
        option_1 = TopicPollOptionFactory.create(poll=poll)
        TopicPollOptionFactory.create(poll=poll)

        # Run & check
        with pytest.raises(ValidationError):
            vote = TopicPollVoteFactory.build(
                poll_option=option_1, voter=self.u1, anonymous_key='ertyue')
            vote.clean()
