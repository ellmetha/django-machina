# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.core.exceptions import ValidationError
from django.db.models import get_model
from django.test import TestCase
from faker import Factory as FakerFactory

# Local application / specific library imports
from machina.core.utils import refresh
from machina.test.factories import build_topic
from machina.test.factories import create_category_forum
from machina.test.factories import create_forum
from machina.test.factories import create_link_forum
from machina.test.factories import create_topic
from machina.test.factories import PostFactory
from machina.test.factories import UserFactory

faker = FakerFactory.create()

Forum = get_model('forum', 'Forum')
Post = get_model('forum_conversation', 'Post')
Profile = get_model('forum_member', 'Profile')
Topic = get_model('forum_conversation', 'Topic')


class TestTopic(TestCase):
    def setUp(self):
        self.u1 = UserFactory.create()

        # Set up a top-level forum, an associated topic and a post
        self.top_level_forum = create_forum()
        self.topic = create_topic(forum=self.top_level_forum, poster=self.u1)
        self.post = PostFactory.create(topic=self.topic, poster=self.u1)

    def test_knows_if_it_is_a_default_topic(self):
        # Run & check
        self.assertTrue(self.topic.is_topic)

    def test_knows_if_it_is_sticky(self):
        # Setup
        sticky_topic = create_topic(
            forum=self.top_level_forum, poster=self.u1,
            type=Topic.TYPE_CHOICES.topic_sticky)
        # Run & check
        self.assertTrue(sticky_topic.is_sticky)

    def test_knows_if_it_is_an_announce(self):
        # Setup
        announce = create_topic(
            forum=self.top_level_forum, poster=self.u1,
            type=Topic.TYPE_CHOICES.topic_announce)
        # Run & check
        self.assertTrue(announce.is_announce)

    def test_knows_if_it_is_locked(self):
        # Run & check
        self.assertFalse(self.topic.is_locked)
        self.topic.status = self.topic.STATUS_CHOICES.topic_locked
        self.topic.save()
        self.assertTrue(self.topic.is_locked)

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

    def test_cannot_tel_tha_a_non_approved_post_is_the_last_post(self):
        # Setup
        new_topic = create_topic(forum=self.top_level_forum, poster=self.u1)
        # Run & check
        middle_post = PostFactory.create(topic=self.topic, poster=self.u1)
        latest_post = PostFactory.create(topic=self.topic, poster=self.u1, approved=False)
        topic = refresh(self.topic)
        self.assertEqual(topic.last_post, middle_post)

    def test_has_the_first_post_name_as_subject(self):
        # Run & check
        self.assertEqual(self.topic.subject, self.post.subject)

    def test_has_the_same_approved_status_as_its_first_post(self):
        # Run & check
        self.assertEqual(self.topic.approved, self.post.approved)
        self.post.approved = False
        self.post.save()
        self.assertEqual(self.topic.approved, self.post.approved)

    def test_saves_its_number_of_posts(self):
        # Run & check
        post = PostFactory.create(topic=self.topic, poster=self.u1)
        initial_count = self.topic.posts.count()
        self.assertEqual(initial_count, self.topic.posts_count)
        post.delete()
        self.assertEqual(initial_count - 1, self.topic.posts_count)

    def test_saves_only_its_number_of_approved_posts(self):
        # Run & check
        post = PostFactory.create(topic=self.topic, poster=self.u1, approved=False)
        initial_count = self.topic.posts.filter(approved=True).count()
        self.assertEqual(initial_count, self.topic.posts_count)
        post.delete()
        self.assertEqual(initial_count, self.topic.posts_count)

    def test_can_not_be_associated_with_a_forum_link_or_a_forum_category(self):
        # Setup
        top_level_cat = create_category_forum()
        top_level_link = create_link_forum()
        # Run & check
        with self.assertRaises(ValidationError):
            new_topic = build_topic(forum=top_level_cat, poster=self.u1)
            new_topic.full_clean()
        with self.assertRaises(ValidationError):
            new_topic = build_topic(forum=top_level_link, poster=self.u1)
            new_topic.full_clean()

    def test_save_can_trigger_the_update_of_the_counters_of_a_new_forum(self):
        # Setup
        new_top_level_forum = create_forum()
        # Run
        self.topic.forum = new_top_level_forum
        self.topic.save()
        # Check
        self.assertEqual(self.topic.forum, new_top_level_forum)
        self.assertEqual(new_top_level_forum.topics_count, 1)
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

    def test_save_triggers_the_update_of_the_member_posts_count_if_the_related_post_is_approved(self):
        # Setup
        post = PostFactory.build(topic=self.topic, poster=self.u1)
        profile = Profile.objects.get(user=self.u1)
        initial_posts_count = profile.posts_count
        # Run
        post.save()
        # Check
        profile = refresh(profile)
        self.assertEqual(profile.posts_count, initial_posts_count + 1)

    def test_save_cannot_trigger_the_update_of_the_member_posts_count_if_the_related_post_is_not_approved(self):
        # Setup
        post = PostFactory.build(topic=self.topic, poster=self.u1, approved=False)
        profile = Profile.objects.get(user=self.u1)
        initial_posts_count = profile.posts_count
        # Run
        post.save()
        # Check
        profile = refresh(profile)
        self.assertEqual(profile.posts_count, initial_posts_count)

    def test_save_trigger_the_update_of_the_member_posts_count_if_the_related_post_switch_to_approved(self):
        # Setup
        post = PostFactory.create(topic=self.topic, poster=self.u1, approved=False)
        profile = Profile.objects.get(user=self.u1)
        initial_posts_count = profile.posts_count
        # Run
        post.approved = True
        post.save()
        # Check
        profile = refresh(profile)
        self.assertEqual(profile.posts_count, initial_posts_count + 1)