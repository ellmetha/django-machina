# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.db.models import get_model
from django.test import TestCase
from guardian.shortcuts import assign_perm

# Local application / specific library imports
from machina.apps.conversation.forms import PostForm
from machina.conf import settings as machina_settings
from machina.core.loading import get_class
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

        # Set up a top-level forum and a link forum
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
