# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.db.models import get_model
from django.test import TestCase
from faker import Factory as FakerFactory
from guardian.shortcuts import assign_perm

# Local application / specific library imports
from machina.apps.conversation.forms import PostForm
from machina.apps.conversation.forms import TopicForm
from machina.conf import settings as machina_settings
from machina.core.loading import get_class
from machina.core.utils import refresh
from machina.test.factories import create_forum
from machina.test.factories import create_topic
from machina.test.factories import PostFactory
from machina.test.factories import UserFactory

faker = FakerFactory.create()

ForumReadTrack = get_model('tracking', 'ForumReadTrack')
Post = get_model('conversation', 'Post')
Topic = get_model('conversation', 'Topic')
TopicReadTrack = get_model('tracking', 'TopicReadTrack')

PermissionHandler = get_class('permission.handler', 'PermissionHandler')


class TestPostForm(TestCase):
    def setUp(self):
        # Permission handler
        self.perm_handler = PermissionHandler()

        # Create a basic user
        self.user = UserFactory.create()

        # Set up a top-level forum
        self.top_level_forum = create_forum()

        # Set up a topic and some posts
        self.topic = create_topic(forum=self.top_level_forum, poster=self.user)
        self.post = PostFactory.create(topic=self.topic, poster=self.user)

        # Assign some permissions
        assign_perm('can_read_forum', self.user, self.top_level_forum)
        assign_perm('can_start_new_topics', self.user, self.top_level_forum)

    def test_can_valid_a_basic_post(self):
        # Setup
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
        # Check
        self.assertTrue(valid)

    def test_can_affect_a_default_subject_to_the_post(self):
        # Setup
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
        # Check
        default_subject = '{} {}'.format(
            machina_settings.TOPIC_ANSWER_SUBJECT_PREFIX,
            self.topic.subject)
        self.assertEqual(form.fields['subject'].initial, default_subject)

    def test_increments_the_post_updates_counter_in_case_of_post_edition(self):
        # Setup
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
        self.assertTrue(form.is_valid())
        form.save()
        self.post = refresh(self.post)
        self.assertEqual(self.post.updates_count, initial_updates_count + 1)

    def test_set_the_topic_as_unapproved_if_the_user_has_not_the_required_permission(self):
        # Setup
        form_data = {
            'subject': faker.text(max_nb_chars=200),
            'content': '[b]{}[/b]'.format(faker.text()),
        }
        # Run
        form = PostForm(
            data=form_data,
            user=self.user,
            user_ip=faker.ipv4(),
            forum=self.top_level_forum,
            topic=self.topic)
        # Check
        self.assertTrue(form.is_valid())
        post = form.save()
        self.assertFalse(post.approved)
        assign_perm('can_post_without_approval', self.user, self.top_level_forum)
        post = form.save()
        self.assertTrue(post.approved)


class TestTopicForm(TestCase):
    def setUp(self):
        # Permission handler
        self.perm_handler = PermissionHandler()

        # Create a basic user
        self.user = UserFactory.create()

        # Set up a top-level forum
        self.top_level_forum = create_forum()

        # Set up a topic and some posts
        self.topic = create_topic(forum=self.top_level_forum, poster=self.user)
        self.post = PostFactory.create(topic=self.topic, poster=self.user)

        # Assign some permissions
        assign_perm('can_read_forum', self.user, self.top_level_forum)
        assign_perm('can_start_new_topics', self.user, self.top_level_forum)

    def test_can_valid_a_basic_topic(self):
        # Setup
        form_data = {
            'subject': faker.text(max_nb_chars=200),
            'content': '[b]{}[/b]'.format(faker.text()),
            'topic_type': Topic.TYPE_CHOICES.topic_post,
        }
        # Run
        form = TopicForm(
            data=form_data,
            user=self.user,
            user_ip=faker.ipv4(),
            forum=self.top_level_forum)
        valid = form.is_valid()
        # Check
        self.assertTrue(valid)

    def test_can_valid_a_basic_sticky_post(self):
        # Setup
        form_data = {
            'subject': faker.text(max_nb_chars=200),
            'content': '[b]{}[/b]'.format(faker.text()),
            'topic_type': Topic.TYPE_CHOICES.topic_sticky,
        }
        assign_perm('can_post_stickies', self.user, self.top_level_forum)
        # Run
        form = TopicForm(
            data=form_data,
            user=self.user,
            user_ip=faker.ipv4(),
            forum=self.top_level_forum)
        valid = form.is_valid()
        # Check
        self.assertTrue(valid)

    def test_can_valid_a_basic_announce(self):
        # Setup
        form_data = {
            'subject': faker.text(max_nb_chars=200),
            'content': '[b]{}[/b]'.format(faker.text()),
            'topic_type': Topic.TYPE_CHOICES.topic_announce,
        }
        assign_perm('can_post_announcements', self.user, self.top_level_forum)
        # Run
        form = TopicForm(
            data=form_data,
            user=self.user,
            user_ip=faker.ipv4(),
            forum=self.top_level_forum)
        valid = form.is_valid()
        # Check
        self.assertTrue(valid)

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
        # Check
        self.assertTrue(valid)
        post = form.save()
        self.assertEqual(post.topic.type, Topic.TYPE_CHOICES.topic_post)

    def test_allows_the_creation_of_stickies_if_the_user_has_required_permission(self):
        # Setup
        form_data = {
            'subject': faker.text(max_nb_chars=200),
            'content': '[b]{}[/b]'.format(faker.text()),
            'topic_type': Topic.TYPE_CHOICES.topic_sticky,
        }
        form_kwargs = {
            'data': form_data,
            'user': self.user,
            'user_ip': faker.ipv4(),
            'forum': self.top_level_forum,
        }
        #  Run & check
        form = TopicForm(**form_kwargs)
        self.assertFalse(form.is_valid())
        choices = [ch[0] for ch in form.fields['topic_type'].choices]
        self.assertNotIn(Topic.TYPE_CHOICES.topic_sticky, choices)
        assign_perm('can_post_stickies', self.user, self.top_level_forum)
        form = TopicForm(**form_kwargs)
        self.assertTrue(form.is_valid())
        choices = [ch[0] for ch in form.fields['topic_type'].choices]
        self.assertIn(Topic.TYPE_CHOICES.topic_sticky, choices)

    def test_allows_the_creation_of_announces_if_the_user_has_required_permission(self):
        # Setup
        form_data = {
            'subject': faker.text(max_nb_chars=200),
            'content': '[b]{}[/b]'.format(faker.text()),
            'topic_type': Topic.TYPE_CHOICES.topic_announce,
        }
        form_kwargs = {
            'data': form_data,
            'user': self.user,
            'user_ip': faker.ipv4(),
            'forum': self.top_level_forum,
        }
        #  Run & check
        form = TopicForm(**form_kwargs)
        self.assertFalse(form.is_valid())
        choices = [ch[0] for ch in form.fields['topic_type'].choices]
        self.assertNotIn(Topic.TYPE_CHOICES.topic_announce, choices)
        assign_perm('can_post_announcements', self.user, self.top_level_forum)
        form = TopicForm(**form_kwargs)
        self.assertTrue(form.is_valid())
        choices = [ch[0] for ch in form.fields['topic_type'].choices]
        self.assertIn(Topic.TYPE_CHOICES.topic_announce, choices)

    def test_can_be_used_to_update_the_topic_type(self):
        # Setup
        form_data = {
            'subject': 'Re: {}'.format(faker.text(max_nb_chars=200)),
            'content': '[b]{}[/b]'.format(faker.text()),
            'topic_type': Topic.TYPE_CHOICES.topic_sticky,
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
        self.assertTrue(form.is_valid())
        form.save()
        self.topic = refresh(self.topic)
        self.assertEqual(self.topic.type, Topic.TYPE_CHOICES.topic_sticky)
