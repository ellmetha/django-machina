# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from faker import Factory as FakerFactory
import pytest

from machina.apps.forum_conversation.forum_polls.forms import TopicPollOptionFormset
from machina.apps.forum_conversation.forum_polls.forms import TopicPollVoteForm
from machina.core.db.models import get_model
from machina.core.loading import get_class
from machina.test.factories import create_forum
from machina.test.factories import create_topic
from machina.test.factories import PostFactory
from machina.test.factories import TopicPollFactory
from machina.test.factories import TopicPollOptionFactory
from machina.test.factories import UserFactory

faker = FakerFactory.create()

ForumReadTrack = get_model('forum_tracking', 'ForumReadTrack')
Post = get_model('forum_conversation', 'Post')
Topic = get_model('forum_conversation', 'Topic')
TopicReadTrack = get_model('forum_tracking', 'TopicReadTrack')

PermissionHandler = get_class('forum_permission.handler', 'PermissionHandler')
assign_perm = get_class('forum_permission.shortcuts', 'assign_perm')


@pytest.mark.django_db
class TestTopicPollOptionFormset(object):
    @pytest.fixture(autouse=True)
    def setup(self):
        # Permission handler
        self.perm_handler = PermissionHandler()

        # Create a basic user
        self.user = UserFactory.create()

        # Set up a top-level forum
        self.top_level_forum = create_forum()

        # Set up some topics and some posts
        self.topic = create_topic(forum=self.top_level_forum, poster=self.user)
        self.post = PostFactory.create(topic=self.topic, poster=self.user)
        self.alt_topic = create_topic(forum=self.top_level_forum, poster=self.user)
        self.alt_post = PostFactory.create(topic=self.alt_topic, poster=self.user)

        # Assign some permissions
        assign_perm('can_read_forum', self.user, self.top_level_forum)
        assign_perm('can_start_new_topics', self.user, self.top_level_forum)

    def test_can_validate_basic_poll_options(self):
        # Setup
        form_data = {
            'form-0-id': '',
            'form-0-text': faker.text(max_nb_chars=100),
            'form-1-id': '',
            'form-1-text': faker.text(max_nb_chars=100),
            'form-INITIAL_FORMS': 0,
            'form-TOTAL_FORMS': 2,
            'form-MAX_NUM_FORMS': 1000,
        }
        # Run
        form = TopicPollOptionFormset(
            data=form_data,
            topic=self.topic)
        valid = form.is_valid()
        # Check
        assert valid

    def test_cannot_validate_less_than_two_options(self):
        # Setup
        form_data = {
            'form-0-id': '',
            'form-0-text': faker.text(max_nb_chars=100),
            'form-INITIAL_FORMS': 0,
            'form-TOTAL_FORMS': 1,
            'form-MAX_NUM_FORMS': 1000,
        }
        # Run
        form = TopicPollOptionFormset(
            data=form_data,
            topic=self.topic)
        valid = form.is_valid()
        # Check
        assert not valid

    def test_cannot_validate_invalid_options(self):
        # Setup
        form_data = {
            'form-0-id': '',
            'form-0-text': faker.text(max_nb_chars=100),
            'form-1-id': '',
            'form-1-text': faker.text(max_nb_chars=100) * 1000,  # Too long
            'form-INITIAL_FORMS': 0,
            'form-TOTAL_FORMS': 2,
            'form-MAX_NUM_FORMS': 1000,
        }
        # Run
        form = TopicPollOptionFormset(
            data=form_data,
            topic=self.topic)
        valid = form.is_valid()
        # Check
        assert not valid

    def test_can_update_options_associated_with_an_existing_poll(self):
        # Setup
        poll = TopicPollFactory.create(topic=self.topic)
        option_1 = TopicPollOptionFactory.create(poll=poll)
        option_2 = TopicPollOptionFactory.create(poll=poll)
        form_data = {
            'form-0-id': option_1.pk,
            'form-0-text': faker.text(max_nb_chars=100),
            'form-1-id': option_2.pk,
            'form-1-text': option_2.text,
            'form-INITIAL_FORMS': 2,
            'form-TOTAL_FORMS': 2,
            'form-MAX_NUM_FORMS': 1000,
        }
        self.topic.refresh_from_db()
        # Run
        form = TopicPollOptionFormset(
            data=form_data,
            topic=self.topic)
        valid = form.is_valid()
        # Check
        assert valid
        form.save()
        option_1.refresh_from_db()
        assert option_1.text == form_data['form-0-text']

    def test_append_empty_forms_only_when_no_initial_data_is_provided(self):
        # Setup
        poll = TopicPollFactory.create(topic=self.topic)
        option_1 = TopicPollOptionFactory.create(poll=poll)
        option_2 = TopicPollOptionFactory.create(poll=poll)
        form_data_1 = {
            'form-0-id': option_1.pk,
            'form-0-text': faker.text(max_nb_chars=100),
            'form-1-id': option_2.pk,
            'form-1-text': option_2.text,
            'form-INITIAL_FORMS': 2,
            'form-TOTAL_FORMS': 2,
            'form-MAX_NUM_FORMS': 1000,
        }
        self.topic.refresh_from_db()
        # Run
        form_1 = TopicPollOptionFormset(
            data=form_data_1,
            topic=self.topic)
        form_2 = TopicPollOptionFormset(topic=self.topic)  # poll already created
        form_3 = TopicPollOptionFormset(topic=self.alt_topic)  # no poll
        # Check
        assert form_1.total_form_count() == 2
        assert form_2.total_form_count() == 2
        assert form_3.total_form_count() == 2


@pytest.mark.django_db
class TestTopicPollVoteForm(object):
    @pytest.fixture(autouse=True)
    def setup(self):
        # Permission handler
        self.perm_handler = PermissionHandler()

        # Create a basic user
        self.user = UserFactory.create()

        # Set up a top-level forum
        self.top_level_forum = create_forum()

        # Set up a topic and some posts
        self.topic = create_topic(forum=self.top_level_forum, poster=self.user)
        self.post = PostFactory.create(topic=self.topic, poster=self.user)

        # Creates a poll and two options
        self.poll = TopicPollFactory.create(topic=self.topic)
        self.option_1 = TopicPollOptionFactory.create(poll=self.poll)
        self.option_2 = TopicPollOptionFactory.create(poll=self.poll)

        # Assign some permissions
        assign_perm('can_read_forum', self.user, self.top_level_forum)
        assign_perm('can_start_new_topics', self.user, self.top_level_forum)

    def test_can_valid_a_basic_vote(self):
        # Setup
        form_data = {
            'options': self.option_1.pk,
        }
        # Run
        form = TopicPollVoteForm(
            data=form_data,
            poll=self.poll)
        valid = form.is_valid()
        # Check
        assert valid

    def test_cannot_validate_empty_votes(self):
        # Setup
        form_data = {}
        # Run
        form = TopicPollVoteForm(
            data=form_data,
            poll=self.poll)
        valid = form.is_valid()
        # Check
        assert not valid

    def test_cannot_validate_votes_for_too_many_options(self):
        # Setup
        self.poll.max_options = 3
        self.poll.save()
        option_3 = TopicPollOptionFactory.create(poll=self.poll)
        option_4 = TopicPollOptionFactory.create(poll=self.poll)
        form_data = {
            'options': [self.option_1.pk, self.option_2.pk, option_3.pk, option_4.pk, ]
        }
        # Run
        form = TopicPollVoteForm(
            data=form_data,
            poll=self.poll)
        valid = form.is_valid()
        # Check
        assert not valid
