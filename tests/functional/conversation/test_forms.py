# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import forms
from django.contrib.auth.models import AnonymousUser
from faker import Factory as FakerFactory
import pytest

from machina.apps.forum_conversation.forms import PostForm
from machina.apps.forum_conversation.forms import TopicForm
from machina.conf import settings as machina_settings
from machina.core.db.models import get_model
from machina.core.loading import get_class
from machina.test.factories import create_forum
from machina.test.factories import create_topic
from machina.test.factories import PostFactory
from machina.test.factories import TopicPollFactory
from machina.test.factories import UserFactory

faker = FakerFactory.create()

ForumReadTrack = get_model('forum_tracking', 'ForumReadTrack')
Post = get_model('forum_conversation', 'Post')
Topic = get_model('forum_conversation', 'Topic')
TopicReadTrack = get_model('forum_tracking', 'TopicReadTrack')

PermissionHandler = get_class('forum_permission.handler', 'PermissionHandler')
assign_perm = get_class('forum_permission.shortcuts', 'assign_perm')


@pytest.mark.django_db
class TestPostForm(object):
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

        # Assign some permissions
        assign_perm('can_read_forum', self.user, self.top_level_forum)
        assign_perm('can_start_new_topics', self.user, self.top_level_forum)

    def test_can_valid_a_basic_post(self):
        # Setup
        form_data = {
            'subject': 'Re: {}'.format(faker.text(max_nb_chars=200)),
            'content': '[b]{}[/b]'.format(faker.text()),
        }
        # Run
        form = PostForm(
            data=form_data,
            user=self.user,
            user_ip=faker.ipv4(),
            forum=self.top_level_forum,
            topic=self.topic)
        valid = form.is_valid()
        # Check
        assert valid

    def test_can_affect_a_default_subject_to_the_post(self):
        # Setup
        form_data = {
            'content': '[b]{}[/b]'.format(faker.text()),
        }
        # Run
        form = PostForm(
            data=form_data,
            user=self.user,
            user_ip=faker.ipv4(),
            forum=self.top_level_forum,
            topic=self.topic)
        # Check
        default_subject = '{} {}'.format(
            machina_settings.TOPIC_ANSWER_SUBJECT_PREFIX,
            self.topic.subject)
        assert form.fields['subject'].initial == default_subject

    def test_increments_the_post_updates_counter_in_case_of_post_edition(self):
        # Setup
        form_data = {
            'subject': 'Re: {}'.format(faker.text(max_nb_chars=200)),
            'content': '[b]{}[/b]'.format(faker.text()),
        }
        initial_updates_count = self.post.updates_count
        # Run
        form = PostForm(
            data=form_data,
            user=self.user,
            user_ip=faker.ipv4(),
            forum=self.top_level_forum,
            topic=self.topic,
            instance=self.post)
        # Check
        assert form.is_valid()
        form.save()
        self.post.refresh_from_db()
        assert self.post.updates_count == initial_updates_count + 1

    def test_set_the_topic_as_unapproved_if_the_user_has_not_the_required_permission(self):
        # Setup
        form_data = {
            'subject': faker.text(max_nb_chars=200),
            'content': '[b]{}[/b]'.format(faker.text()),
        }
        # Run
        form_kwargs = {
            'data': form_data,
            'user': self.user,
            'user_ip': faker.ipv4(),
            'forum': self.top_level_forum,
            'topic': self.topic,
        }
        form = PostForm(**form_kwargs)
        # Check
        assert form.is_valid()
        post = form.save()
        assert not post.approved
        assign_perm('can_post_without_approval', self.user, self.top_level_forum)
        form = PostForm(**form_kwargs)
        assert form.is_valid()
        post = form.save()
        assert post.approved

    def test_adds_the_username_field_if_the_user_is_anonymous(self):
        # Setup
        form_data = {
            'subject': faker.text(max_nb_chars=200),
            'content': '[b]{}[/b]'.format(faker.text()),
            'username': 'testname',
        }
        user = AnonymousUser()
        user.forum_key = '1234'
        # Run
        form = PostForm(
            data=form_data,
            user=user,
            user_ip=faker.ipv4(),
            forum=self.top_level_forum,
            topic=self.topic)
        # Check
        assert 'username' in form.fields
        assert form.is_valid()
        post = form.save()
        assert post.username == 'testname'

    def test_adds_the_update_reason_field_if_the_post_is_updated(self):
        # Setup
        form_data = {
            'subject': faker.text(max_nb_chars=200),
            'content': '[b]{}[/b]'.format(faker.text()),
            'update_reason': 'X',
        }
        # Run
        form = PostForm(
            data=form_data,
            user=self.user,
            user_ip=faker.ipv4(),
            forum=self.top_level_forum,
            topic=self.topic,
            instance=self.post)
        # Check
        assert 'update_reason' in form.fields
        assert form.is_valid()
        post = form.save()
        assert post.update_reason == 'X'


@pytest.mark.django_db
class TestTopicForm(object):
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

        # Assign some permissions
        assign_perm('can_read_forum', self.user, self.top_level_forum)
        assign_perm('can_start_new_topics', self.user, self.top_level_forum)

    def test_can_valid_a_basic_topic(self):
        # Setup
        form_data = {
            'subject': faker.text(max_nb_chars=200),
            'content': '[b]{}[/b]'.format(faker.text()),
            'topic_type': Topic.TOPIC_POST,
        }
        # Run
        form = TopicForm(
            data=form_data,
            user=self.user,
            user_ip=faker.ipv4(),
            forum=self.top_level_forum)
        valid = form.is_valid()
        # Check
        assert valid

    def test_can_valid_a_basic_sticky_post(self):
        # Setup
        form_data = {
            'subject': faker.text(max_nb_chars=200),
            'content': '[b]{}[/b]'.format(faker.text()),
            'topic_type': Topic.TOPIC_STICKY,
        }
        assign_perm('can_post_stickies', self.user, self.top_level_forum)
        # Run
        form = TopicForm(
            data=form_data,
            user=self.user,
            user_ip=faker.ipv4(),
            forum=self.top_level_forum)
        valid = form.is_valid()
        # Check
        assert valid

    def test_can_valid_a_basic_announce(self):
        # Setup
        form_data = {
            'subject': faker.text(max_nb_chars=200),
            'content': '[b]{}[/b]'.format(faker.text()),
            'topic_type': Topic.TOPIC_ANNOUNCE,
        }
        assign_perm('can_post_announcements', self.user, self.top_level_forum)
        # Run
        form = TopicForm(
            data=form_data,
            user=self.user,
            user_ip=faker.ipv4(),
            forum=self.top_level_forum)
        valid = form.is_valid()
        # Check
        assert valid

    def test_creates_a_post_topic_if_no_topic_type_is_provided(self):
        # Setup
        form_data = {
            'subject': '{}'.format(faker.text(max_nb_chars=200)),
            'content': '[b]{}[/b]'.format(faker.text()),
        }
        # Run
        form = TopicForm(
            data=form_data,
            user=self.user,
            user_ip=faker.ipv4(),
            forum=self.top_level_forum)
        valid = form.is_valid()
        # Check
        assert valid
        post = form.save()
        assert post.topic.type == Topic.TOPIC_POST

    def test_allows_the_creation_of_stickies_if_the_user_has_required_permission(self):
        # Setup
        form_data = {
            'subject': faker.text(max_nb_chars=200),
            'content': '[b]{}[/b]'.format(faker.text()),
            'topic_type': Topic.TOPIC_STICKY,
        }
        form_kwargs = {
            'data': form_data,
            'user': self.user,
            'user_ip': faker.ipv4(),
            'forum': self.top_level_forum,
        }
        # Run & check
        form = TopicForm(**form_kwargs)
        assert not form.is_valid()
        choices = [ch[0] for ch in form.fields['topic_type'].choices]
        assert Topic.TOPIC_STICKY not in choices
        assign_perm('can_post_stickies', self.user, self.top_level_forum)
        form = TopicForm(**form_kwargs)
        assert form.is_valid()
        choices = [ch[0] for ch in form.fields['topic_type'].choices]
        assert Topic.TOPIC_STICKY in choices

    def test_allows_the_creation_of_announces_if_the_user_has_required_permission(self):
        # Setup
        form_data = {
            'subject': faker.text(max_nb_chars=200),
            'content': '[b]{}[/b]'.format(faker.text()),
            'topic_type': Topic.TOPIC_ANNOUNCE,
        }
        form_kwargs = {
            'data': form_data,
            'user': self.user,
            'user_ip': faker.ipv4(),
            'forum': self.top_level_forum,
        }
        # Run & check
        form = TopicForm(**form_kwargs)
        assert not form.is_valid()
        choices = [ch[0] for ch in form.fields['topic_type'].choices]
        assert Topic.TOPIC_ANNOUNCE not in choices
        assign_perm('can_post_announcements', self.user, self.top_level_forum)
        form = TopicForm(**form_kwargs)
        assert form.is_valid()
        choices = [ch[0] for ch in form.fields['topic_type'].choices]
        assert Topic.TOPIC_ANNOUNCE in choices

    def test_can_be_used_to_update_the_topic_type(self):
        # Setup
        form_data = {
            'subject': 'Re: {}'.format(faker.text(max_nb_chars=200)),
            'content': '[b]{}[/b]'.format(faker.text()),
            'topic_type': Topic.TOPIC_STICKY,
        }
        assign_perm('can_post_stickies', self.user, self.top_level_forum)
        # Run
        form = TopicForm(
            data=form_data,
            user=self.user,
            user_ip=faker.ipv4(),
            forum=self.top_level_forum,
            topic=self.topic,
            instance=self.post)
        # Check
        assert form.is_valid()
        form.save()
        self.topic.refresh_from_db()
        assert self.topic.type == Topic.TOPIC_STICKY

    def test_can_append_poll_fields_if_the_user_is_allowed_to_create_polls(self):
        # Setup
        form_data = {
            'subject': 'Re: {}'.format(faker.text(max_nb_chars=200)),
            'content': '[b]{}[/b]'.format(faker.text()),
            'topic_type': Topic.TOPIC_STICKY,
        }
        assign_perm('can_create_polls', self.user, self.top_level_forum)
        # Run
        form = TopicForm(
            data=form_data,
            user=self.user,
            user_ip=faker.ipv4(),
            forum=self.top_level_forum,
            topic=self.topic,
            instance=self.post)
        # Check
        assert 'poll_question' in form.fields
        assert 'poll_max_options' in form.fields
        assert 'poll_duration' in form.fields
        assert 'poll_user_changes' in form.fields
        assert isinstance(form.fields['poll_question'], forms.CharField)
        assert isinstance(form.fields['poll_max_options'], forms.IntegerField)
        assert isinstance(form.fields['poll_duration'], forms.IntegerField)
        assert isinstance(form.fields['poll_user_changes'], forms.BooleanField)

    def test_cannot_append_poll_fields_if_the_user_is_not_allowed_to_create_polls(self):
        # Setup
        form_data = {
            'subject': 'Re: {}'.format(faker.text(max_nb_chars=200)),
            'content': '[b]{}[/b]'.format(faker.text()),
            'topic_type': Topic.TOPIC_STICKY,
        }
        # Run
        form = TopicForm(
            data=form_data,
            user=self.user,
            user_ip=faker.ipv4(),
            forum=self.top_level_forum,
            topic=self.topic,
            instance=self.post)
        # Check
        assert 'poll_question' not in form.fields
        assert 'poll_max_options' not in form.fields
        assert 'poll_duration' not in form.fields
        assert 'poll_user_changes' not in form.fields

    def test_can_initialize_poll_fields_from_topic_related_poll_object(self):
        # Setup
        form_data = {
            'subject': 'Re: {}'.format(faker.text(max_nb_chars=200)),
            'content': '[b]{}[/b]'.format(faker.text()),
            'topic_type': Topic.TOPIC_STICKY,
        }
        assign_perm('can_create_polls', self.user, self.top_level_forum)
        poll = TopicPollFactory.create(topic=self.post.topic)
        # Run
        form = TopicForm(
            data=form_data,
            user=self.user,
            user_ip=faker.ipv4(),
            forum=self.top_level_forum,
            topic=self.topic,
            instance=self.post)
        # Check
        assert 'poll_question' in form.fields
        assert 'poll_max_options' in form.fields
        assert 'poll_duration' in form.fields
        assert 'poll_user_changes' in form.fields
        assert form.fields['poll_question'].initial == poll.question
        assert form.fields['poll_max_options'].initial == poll.max_options
        assert form.fields['poll_duration'].initial == poll.duration
        assert form.fields['poll_user_changes'].initial == poll.user_changes
