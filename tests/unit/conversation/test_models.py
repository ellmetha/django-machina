# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.contrib.auth.models import User
from django.db.models import get_model
from django.test import TestCase

# Local application / specific library imports
from machina.apps.conversation.abstract_models import TOPIC_STATUSES
from machina.apps.conversation.abstract_models import TOPIC_TYPES
from machina.apps.forum.abstract_models import FORUM_TYPES
Forum = get_model('forum', 'Forum')
Post = get_model('conversation', 'Post')
Topic = get_model('conversation', 'Topic')


class TestTopic(TestCase):
    def setUp(self):
        self.u1 = User.objects.create(username='user1')

        # Set up a top-level forum
        top_level_forum = Forum.objects.create(name='top_level_forum', type=FORUM_TYPES.forum_post)
        self.top_level_forum = top_level_forum

        # Set up a topic
        topic = Topic.objects.create(subject='Test topic', forum=self.top_level_forum, poster=self.u1,
                                     type=TOPIC_TYPES.topic_post, status=TOPIC_STATUSES.topic_unlocked)
        self.topic = topic

        # Set up a post
        post = Post.objects.create(topic=self.topic, poster=self.u1, content='hello')
        self.post = post

    def test_has_a_first_post(self):
        # Run & check
        self.assertEqual(self.topic.first_post, self.post)
        Post.objects.create(topic=self.topic, poster=self.u1, content='hello')
        self.assertEqual(self.topic.first_post, self.post)

    def test_has_a_last_post(self):
        # Setup
        new_topic = Topic.objects.create(subject='Test topic', forum=self.top_level_forum, poster=self.u1,
                                         type=TOPIC_TYPES.topic_post, status=TOPIC_STATUSES.topic_unlocked)
        # Run & check
        middle_post = Post.objects.create(topic=self.topic, poster=self.u1, content='hello')
        self.assertEqual(self.topic.last_post, middle_post)
        new_last_post = Post.objects.create(topic=self.topic, poster=self.u1, content='last')
        self.assertEqual(self.topic.last_post, new_last_post)
        self.assertIsNone(new_topic.last_post)

    def test_saves_its_number_of_posts(self):
        # Run
        Post.objects.create(topic=self.topic, poster=self.u1, content='hello')
        # Check
        self.assertEqual(self.topic.posts.count(), self.topic.posts_count)

    def test_has_an_update_date(self):
        # Run & check
        Post.objects.create(topic=self.topic, poster=self.u1, content='hello')
        self.assertEqual(self.topic.updated.replace(microsecond=0), self.topic.last_post.created.replace(microsecond=0))
        self.topic.last_post.content = 'updated'
        self.topic.last_post.save()
        self.assertEqual(self.topic.updated.replace(microsecond=0), self.topic.last_post.created.replace(microsecond=0))
