# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
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
        # Run & check
        post = Post.objects.create(topic=self.topic, poster=self.u1, content='hello')
        initial_count = self.topic.posts.count()
        self.assertEqual(initial_count, self.topic.posts_count)
        post.delete()
        self.assertEqual(initial_count - 1, self.topic.posts_count)

    def test_can_not_be_associated_with_a_forum_link_or_a_forum_category(self):
        # Setup
        top_level_cat = Forum.objects.create(name='top_level_cat', type=FORUM_TYPES.forum_cat)
        top_level_link = Forum.objects.create(name='top_level_link', type=FORUM_TYPES.forum_link)
        # Run & check
        with self.assertRaises(ValidationError):
            new_topic = Topic(subject='Test topic', forum=top_level_cat, poster=self.u1,
                              type=TOPIC_TYPES.topic_post, status=TOPIC_STATUSES.topic_unlocked)
            new_topic.full_clean()
        with self.assertRaises(ValidationError):
            new_topic = Topic(subject='Test topic', forum=top_level_link, poster=self.u1,
                              type=TOPIC_TYPES.topic_post, status=TOPIC_STATUSES.topic_unlocked)
            new_topic.full_clean()

    def test_can_trigger_the_update_of_the_counters_of_a_new_forum(self):
        # Setup
        new_top_level_forum = Forum.objects.create(name='new_top_level_forum', type=FORUM_TYPES.forum_post)
        # Run
        self.topic.forum = new_top_level_forum
        self.topic.save()
        # Check
        self.assertEqual(self.topic.forum, new_top_level_forum)
        self.assertEqual(new_top_level_forum.topics_count, 1)
        self.assertEqual(new_top_level_forum.real_topics_count, 1)
        self.assertEqual(new_top_level_forum.posts_count, self.topic.posts_count)


class TestPost(TestCase):
    def setUp(self):
        self.u1 = User.objects.create(username='user1')

        # Set up a top-level forum
        top_level_forum = Forum.objects.create(name='top_level_forum', type=FORUM_TYPES.forum_post)
        self.top_level_forum = top_level_forum

        # Set up a topic
        topic = Topic.objects.create(subject='Test topic', forum=self.top_level_forum, poster=self.u1,
                                     type=TOPIC_TYPES.topic_post, status=TOPIC_STATUSES.topic_unlocked)
        self.topic = topic
        self.topic_pk = topic.pk

        # Set up a post
        post = Post.objects.create(topic=self.topic, poster=self.u1, content='hello')
        self.post = post

    def test_knows_if_it_is_the_topic_head(self):
        # Check
        self.assertEqual(self.post.is_topic_head, self.post.topic.posts.count() == 1)

    def test_knows_if_it_is_the_topic_tail(self):
        # Run & check
        post = Post.objects.create(topic=self.topic, poster=self.u1, content='hello')
        self.assertTrue(post.is_topic_tail)

    def test_is_both_topic_head_and_tail_if_it_is_alone_in_the_topic(self):
        # Check
        self.assertTrue(self.post.is_topic_head)
        self.assertTrue(self.post.is_topic_tail)

    def test_deletion_should_result_in_the_topic_deletion_if_it_is_alone_in_the_topic(self):
        # Run
        self.post.delete()
        # Check
        with self.assertRaises(Topic.DoesNotExist):
            Topic.objects.get(pk=self.topic_pk)
