# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.core.exceptions import ValidationError
from django.db.models import get_model
from django.test import TestCase

# Local application / specific library imports
from machina.test.factories import build_topic
from machina.test.factories import create_category_forum
from machina.test.factories import create_forum
from machina.test.factories import create_link_forum
from machina.test.factories import create_topic
from machina.test.factories import PostFactory
from machina.test.factories import UserFactory

Forum = get_model('forum', 'Forum')
Post = get_model('conversation', 'Post')
Topic = get_model('conversation', 'Topic')


class TestTopic(TestCase):
    def setUp(self):
        self.u1 = UserFactory.create()

        # Set up a top-level forum, an associated topic and a post
        self.top_level_forum = create_forum()
        self.topic = create_topic(forum=self.top_level_forum, poster=self.u1)
        self.post = PostFactory.create(topic=self.topic, poster=self.u1)

    def test_has_a_first_post(self):
        # Run & check
        self.assertEqual(self.topic.first_post, self.post)
        PostFactory.create(topic=self.topic, poster=self.u1)
        self.assertEqual(self.topic.first_post, self.post)

    def test_has_a_last_post(self):
        # Setup
        new_topic = create_topic(forum=self.top_level_forum, poster=self.u1)
        # Run & check
        middle_post = PostFactory.create(topic=self.topic, poster=self.u1)
        self.assertEqual(self.topic.last_post, middle_post)
        new_last_post = Post.objects.create(topic=self.topic, poster=self.u1, content='last')
        self.assertEqual(self.topic.last_post, new_last_post)
        self.assertIsNone(new_topic.last_post)

    def test_has_the_first_post_name_as_subject(self):
        # Run & check
        self.assertEqual(self.topic.subject, self.post.subject)

    def test_saves_its_number_of_posts(self):
        # Run & check
        post = PostFactory.create(topic=self.topic, poster=self.u1)
        initial_count = self.topic.posts.count()
        self.assertEqual(initial_count, self.topic.posts_count)
        post.delete()
        self.assertEqual(initial_count - 1, self.topic.posts_count)

    def test_can_not_be_associated_with_a_forum_link_or_a_forum_category(self):
        # Setup
        top_level_cat = create_category_forum()
        top_level_link = create_link_forum()
        # Run & check
        with self.assertRaises(ValidationError):
            new_topic = build_topic(forum=top_level_cat, poster=self.u1)
            new_topic.full_clean()
        with self.assertRaises(ValidationError):
            new_topic = new_topic = build_topic(forum=top_level_link, poster=self.u1)
            new_topic.full_clean()

    def test_can_trigger_the_update_of_the_counters_of_a_new_forum(self):
        # Setup
        new_top_level_forum = create_forum()
        # Run
        self.topic.forum = new_top_level_forum
        self.topic.save()
        # Check
        self.assertEqual(self.topic.forum, new_top_level_forum)
        self.assertEqual(new_top_level_forum.topics_count, 1)
        self.assertEqual(new_top_level_forum.real_topics_count, 1)
        self.assertEqual(new_top_level_forum.posts_count, self.topic.posts_count)

    def test_can_trigger_the_update_of_the_counters_of_a_previous_forum(self):
        # Setup
        new_top_level_forum = create_forum()
        # Run
        self.topic.forum = new_top_level_forum
        self.topic.save()
        # Check
        self.top_level_forum = Forum.objects.get(pk=self.top_level_forum.pk)  # Reload the forum from DB
        self.assertEqual(self.topic.forum, new_top_level_forum)
        self.assertEqual(self.top_level_forum.topics_count, 0)
        self.assertEqual(self.top_level_forum.real_topics_count, 0)
        self.assertEqual(self.top_level_forum.posts_count, 0)


class TestPost(TestCase):
    def setUp(self):
        self.u1 = UserFactory.create()

        # Set up a top-level forum, an associated topic and a post
        self.top_level_forum = create_forum()
        self.topic = create_topic(forum=self.top_level_forum, poster=self.u1)
        self.post = PostFactory.create(topic=self.topic, poster=self.u1)

        self.topic_pk = self.topic.pk

    def test_knows_if_it_is_the_topic_head(self):
        # Check
        self.assertEqual(self.post.is_topic_head, self.post.topic.posts.count() == 1)

    def test_knows_if_it_is_the_topic_tail(self):
        # Run & check
        post = PostFactory.create(topic=self.topic, poster=self.u1)
        self.assertTrue(post.is_topic_tail)

    def test_knows_its_position_inside_the_topic(self):
        # Setup
        post_2 = PostFactory.create(topic=self.topic, poster=self.u1)
        post_3 = PostFactory.create(topic=self.topic, poster=self.u1)
        # Run & check
        self.assertEqual(self.post.position, 1)
        self.assertEqual(post_2.position, 2)
        self.assertEqual(post_3.position, 3)

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
