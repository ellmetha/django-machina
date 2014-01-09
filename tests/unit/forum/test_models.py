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


class TestForum(TestCase):
    def setUp(self):
        self.u1 = User.objects.create(username='user1')

        # Set up a top-level category
        top_level_cat = Forum.objects.create(name='top_level_cat', type=FORUM_TYPES.forum_cat)
        self.top_level_cat = top_level_cat

        # Set up a top-level forum
        top_level_forum = Forum.objects.create(name='top_level_forum', type=FORUM_TYPES.forum_post)
        self.top_level_forum = top_level_forum

        # Set up a top-level forum link
        top_level_link = Forum.objects.create(name='top_level_link', type=FORUM_TYPES.forum_link)
        self.top_level_link = top_level_link

    def test_has_a_margin_level_two_times_greater_than_its_real_level(self):
        # Run
        sub_level_forum = Forum(parent=self.top_level_forum,
                                name='sub_level_forum', type=FORUM_TYPES.forum_post)
        sub_level_forum.full_clean()
        sub_level_forum.save()
        # Check
        self.assertEqual(self.top_level_forum.margin_level, 0)
        self.assertEqual(sub_level_forum.margin_level, 2)

    def test_can_not_be_the_child_of_a_forum_link(self):
        # Run & check
        for forum_type, _ in FORUM_TYPES:
            with self.assertRaises(ValidationError):
                forum = Forum(parent=self.top_level_link, name='sub_forum', type=forum_type)
                forum.full_clean()

    def test_must_have_a_link_in_case_of_a_link_forum(self):
        # Run & check
        with self.assertRaises(ValidationError):
            forum = Forum(parent=self.top_level_forum, name='sub_link_forum', type=FORUM_TYPES.forum_link)
            forum.full_clean()

    def test_saves_its_numbers_of_posts_and_topics(self):
        # Run & check
        topic = Topic.objects.create(subject='Test topic', forum=self.top_level_forum, poster=self.u1,
                                     type=TOPIC_TYPES.topic_post, status=TOPIC_STATUSES.topic_unlocked)
        Post.objects.create(topic=topic, poster=self.u1, content='hello')
        Post.objects.create(topic=topic, poster=self.u1, content='hello2')
        self.assertEqual(self.top_level_forum.posts_count, topic.posts.count())
        self.assertEqual(self.top_level_forum.topics_count, self.top_level_forum.topics.count())
        self.assertEqual(self.top_level_forum.real_topics_count, self.top_level_forum.topics.count())
        topic2 = Topic.objects.create(subject='Test topic 2', forum=self.top_level_forum, poster=self.u1,
                                      type=TOPIC_TYPES.topic_post, status=TOPIC_STATUSES.topic_unlocked,
                                      approved=False)
        Post.objects.create(topic=topic2, poster=self.u1, content='hello')
        self.assertEqual(self.top_level_forum.posts_count, topic.posts.count() + topic2.posts.count())
        self.assertEqual(self.top_level_forum.topics_count,
                         self.top_level_forum.topics.filter(approved=True).count())
        self.assertEqual(self.top_level_forum.real_topics_count, self.top_level_forum.topics.count())

    def test_can_indicate_its_appartenance_to_a_forum_type(self):
        # Run & check
        self.assertTrue(self.top_level_cat.is_category)
        self.assertTrue(self.top_level_forum.is_forum)
        self.assertTrue(self.top_level_link.is_link)

    def test_can_trigger_the_update_of_the_counters_of_a_new_parent(self):
        # Setup
        topic = Topic.objects.create(subject='Test topic', forum=self.top_level_forum, poster=self.u1,
                                     type=TOPIC_TYPES.topic_post, status=TOPIC_STATUSES.topic_unlocked)
        Post.objects.create(topic=topic, poster=self.u1, content='hello')
        Post.objects.create(topic=topic, poster=self.u1, content='hello2')
        # Run
        self.top_level_forum.parent = self.top_level_cat
        self.top_level_forum.save()
        # Check
        self.assertEqual(self.top_level_cat.posts_count, self.top_level_forum.posts_count)
        self.assertEqual(self.top_level_cat.topics_count, self.top_level_forum.topics_count)
        self.assertEqual(self.top_level_cat.real_topics_count, self.top_level_forum.real_topics_count)
