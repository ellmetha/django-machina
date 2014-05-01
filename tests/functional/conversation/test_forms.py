# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.db.models import get_model
from django.test import TestCase
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
            'subject': 'Re: topic',
            'content': '[b]This is a revolution[/b]',
        }
        # Run
        form = PostForm(
            data=form_data,
            user=self.user,
            user_ip='127.0.0.1',
            forum=self.top_level_forum,
            topic=self.topic)
        valid = form.is_valid()
        # Check
        self.assertTrue(valid)

    def test_can_affect_a_default_subject_to_the_post(self):
        # Setup
        form_data = {
            'content': '[b]This is a revolution[/b]',
        }
        # Run
        form = PostForm(
            data=form_data,
            user=self.user,
            user_ip='127.0.0.1',
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
            'subject': 'My new topic subject',
            'content': '[b]This is a revolution[/b]',
        }
        initial_updates_count = self.post.updates_count
        # Run
        form = PostForm(
            data=form_data,
            user=self.user,
            user_ip='127.0.0.1',
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
            'subject': 'My new topic subject',
            'content': '[b]This is a revolution[/b]',
        }
        # Run
        form = PostForm(
            data=form_data,
            user=self.user,
            user_ip='127.0.0.1',
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
            'subject': 'Re: topic',
            'content': '[b]This is a revolution[/b]',
            'topic_type': Topic.TYPE_CHOICES.topic_post,
        }
        # Run
        form = TopicForm(
            data=form_data,
            user=self.user,
            user_ip='127.0.0.1',
            forum=self.top_level_forum)
        valid = form.is_valid()
        # Check
        self.assertTrue(valid)

    def test_can_valid_a_basic_sticky_post(self):
        # Setup
        form_data = {
            'subject': 'Re: topic',
            'content': '[b]This is a revolution[/b]',
            'topic_type': Topic.TYPE_CHOICES.topic_sticky,
        }
        assign_perm('can_post_stickies', self.user, self.top_level_forum)
        # Run
        form = TopicForm(
            data=form_data,
            user=self.user,
            user_ip='127.0.0.1',
            forum=self.top_level_forum)
        valid = form.is_valid()
        # Check
        self.assertTrue(valid)

    def test_can_valid_a_basic_announce(self):
        # Setup
        form_data = {
            'subject': 'Re: topic',
            'content': '[b]This is a revolution[/b]',
            'topic_type': Topic.TYPE_CHOICES.topic_announce,
        }
        assign_perm('can_post_announcements', self.user, self.top_level_forum)
        # Run
        form = TopicForm(
            data=form_data,
            user=self.user,
            user_ip='127.0.0.1',
            forum=self.top_level_forum)
        valid = form.is_valid()
        # Check
        self.assertTrue(valid)
