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


class TopicTestCase(TestCase):
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

    def test_topic_first_post(self):
        """
        Tests that the first post returned by a topic is realy the oldest post associated
        with the considered topic and that it remains even if new posts are added to the topic.
        """
        # Run & check
        self.assertEqual(self.topic.first_post, self.post)
        Post.objects.create(topic=self.topic, poster=self.u1, content='hello')
        self.assertEqual(self.topic.first_post, self.post)

    def test_topic_last_post(self):
        """
        Tests that the last post returned by a topic is realy the youngest post associated
        with the considered topic and that it is updated if a new post is added to the topic.
        """
        # Setup
        new_topic = Topic.objects.create(subject='Test topic', forum=self.top_level_forum, poster=self.u1,
                                         type=TOPIC_TYPES.topic_post, status=TOPIC_STATUSES.topic_unlocked)
        # Run & check
        middle_post = Post.objects.create(topic=self.topic, poster=self.u1, content='hello')
        self.assertEqual(self.topic.last_post, middle_post)
        new_last_post = Post.objects.create(topic=self.topic, poster=self.u1, content='last')
        self.assertEqual(self.topic.last_post, new_last_post)
        self.assertIsNone(new_topic.last_post)

    def test_topic_tracker_data_update(self):
        """
        Tests that the number of posts included in a given topic is correctly saved
        in the 'post_count' field associated with any topic.
        """
        # Run
        Post.objects.create(topic=self.topic, poster=self.u1, content='hello')
        # Check
        self.assertEqual(self.topic.posts.count(), self.topic.posts_count)
