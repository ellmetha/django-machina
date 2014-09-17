# -*- coding: utf-8 -*-

# Standard library imports
import datetime

# Third party imports
from django.db.models import get_model
from guardian.shortcuts import assign_perm
from guardian.shortcuts import remove_perm

# Local application / specific library imports
from machina.core.loading import get_class
from machina.test.factories import create_category_forum
from machina.test.factories import create_forum
from machina.test.factories import create_link_forum
from machina.test.factories import create_topic
from machina.test.factories import GroupFactory
from machina.test.factories import PostFactory
from machina.test.factories import TopicPollFactory
from machina.test.factories import TopicPollOptionFactory
from machina.test.factories import TopicPollVoteFactory
from machina.test.factories import UserFactory
from machina.test.testcases import BaseUnitTestCase

Forum = get_model('forum', 'Forum')
Post = get_model('conversation', 'Post')
Topic = get_model('conversation', 'Topic')

PermissionHandler = get_class('permission.handler', 'PermissionHandler')


class TestPermissionHandler(BaseUnitTestCase):
    def setUp(self):
        self.u1 = UserFactory.create()
        self.g1 = GroupFactory.create()
        self.u1.groups.add(self.g1)

        # Permission handler
        self.perm_handler = PermissionHandler()

        # Set up a top-level category
        self.top_level_cat = create_category_forum()

        # Set up some forums
        self.forum_1 = create_forum(parent=self.top_level_cat)
        self.forum_2 = create_forum(parent=self.top_level_cat)
        self.forum_3 = create_link_forum(parent=self.top_level_cat)

        # Set up a top-level forum link
        self.top_level_link = create_link_forum()

        # Set up some topics
        self.forum_1_topic = create_topic(forum=self.forum_1, poster=self.u1)
        self.forum_3_topic = create_topic(forum=self.forum_3, poster=self.u1)

        # Set up some posts
        self.post_1 = PostFactory.create(topic=self.forum_1_topic, poster=self.u1)
        self.post_2 = PostFactory.create(topic=self.forum_3_topic, poster=self.u1)

        # Assign some permissions
        assign_perm('can_see_forum', self.u1, self.top_level_cat)
        assign_perm('can_see_forum', self.u1, self.forum_1)
        assign_perm('can_read_forum', self.g1, self.forum_3)

    def test_shows_a_forum_if_it_is_visible(self):
        # Setup
        forums = Forum.objects.filter(pk=self.top_level_cat.pk)
        # Run
        filtered_forums = self.perm_handler.forum_list_filter(forums, self.u1)
        # Check
        self.assertQuerysetEqual(filtered_forums, [self.top_level_cat, ])

    def test_hide_a_forum_if_it_is_not_visible(self):
        # Setup
        forums = Forum.objects.filter(pk=self.top_level_cat.pk)
        # Run
        filtered_forums = self.perm_handler.forum_list_filter(forums, self.u1)
        # Check
        self.assertQuerysetEqual(filtered_forums, [self.top_level_cat, ])

    def test_shows_a_forum_if_all_of_its_ancestors_are_visible(self):
        # Setup
        forums = Forum.objects.filter(parent=self.top_level_cat)
        # Run
        filtered_forums = self.perm_handler.forum_list_filter(forums, self.u1)
        # Check
        self.assertQuerysetEqual(filtered_forums, [self.forum_1, self.forum_3])

    def test_hide_a_forum_if_one_of_its_ancestors_is_not_visible(self):
        # Setup
        remove_perm('can_see_forum', self.u1, self.top_level_cat)
        forums = Forum.objects.filter(parent=self.top_level_cat)
        # Run
        filtered_forums = self.perm_handler.forum_list_filter(forums, self.u1)
        # Check
        self.assertQuerysetEqual(filtered_forums, [])

    def test_knows_the_last_topic_visible_inside_a_forum(self):
        # Run & check : no forum hidden
        last_post = self.perm_handler.get_forum_last_post(self.top_level_cat, self.u1)
        self.assertEqual(last_post, self.post_2)

        # Run & check : one forum hidden
        remove_perm('can_read_forum', self.g1, self.forum_3)
        last_post = self.perm_handler.get_forum_last_post(self.top_level_cat, self.u1)
        self.assertEqual(last_post, self.post_1)

        # Run & check : all forums hidden
        remove_perm('can_see_forum', self.u1, self.forum_1)
        last_post = self.perm_handler.get_forum_last_post(self.top_level_cat, self.u1)
        self.assertIsNone(last_post)

    def test_shows_all_forums_to_a_superuser(self):
        # Setup
        u2 = UserFactory.create(is_superuser=True)
        forums = Forum.objects.filter(parent=self.top_level_cat)
        # Run
        filtered_forums = self.perm_handler.forum_list_filter(forums, u2)
        # Check
        self.assertQuerysetEqual(filtered_forums, [self.forum_1, self.forum_2, self.forum_3])

    def test_knows_that_a_superuser_can_edit_all_posts(self):
        # Setup
        u2 = UserFactory.create(is_superuser=True)
        # Run & check
        self.assertTrue(self.perm_handler.can_edit_post(self.post_1, u2))

    def test_knows_if_an_owner_of_a_post_can_edit_it(self):
        # Setup
        u2 = UserFactory.create()
        assign_perm('can_edit_own_posts', self.u1, self.forum_1)
        assign_perm('can_edit_own_posts', u2, self.forum_1)
        # Run & check
        self.assertTrue(self.perm_handler.can_edit_post(self.post_1, self.u1))
        self.assertFalse(self.perm_handler.can_edit_post(self.post_2, self.u1))
        self.assertFalse(self.perm_handler.can_edit_post(self.post_1, u2))

    def test_knows_if_a_moderator_can_edit_a_post(self):
        # Setup
        moderator = UserFactory.create()
        assign_perm('can_edit_posts', moderator, self.forum_1)
        # Run & check
        self.assertTrue(self.perm_handler.can_edit_post(self.post_1, moderator))
        self.assertFalse(self.perm_handler.can_edit_post(self.post_2, moderator))

    def test_knows_that_a_superuser_can_delete_all_posts(self):
        # Setup
        u2 = UserFactory.create(is_superuser=True)
        # Run & check
        self.assertTrue(self.perm_handler.can_delete_post(self.post_1, u2))

    def test_knows_if_an_owner_of_a_post_can_delete_it(self):
        # Setup
        u2 = UserFactory.create()
        assign_perm('can_delete_own_posts', self.u1, self.forum_1)
        assign_perm('can_delete_own_posts', u2, self.forum_1)
        # Run & check
        self.assertTrue(self.perm_handler.can_delete_post(self.post_1, self.u1))
        self.assertFalse(self.perm_handler.can_delete_post(self.post_2, self.u1))
        self.assertFalse(self.perm_handler.can_delete_post(self.post_1, u2))

    def test_knows_if_a_moderator_can_delete_a_post(self):
        # Setup
        moderator = UserFactory.create()
        assign_perm('can_delete_posts', moderator, self.forum_1)
        # Run & check
        self.assertTrue(self.perm_handler.can_delete_post(self.post_1, moderator))
        self.assertFalse(self.perm_handler.can_delete_post(self.post_2, moderator))

    def test_knows_if_a_user_can_add_stickies(self):
        # Setup
        u2 = UserFactory.create()
        assign_perm('can_post_stickies', self.u1, self.forum_1)
        # Run & check
        self.assertTrue(self.perm_handler.can_add_stickies(self.forum_1, self.u1))
        self.assertFalse(self.perm_handler.can_add_stickies(self.forum_1, u2))

    def test_knows_that_a_superuser_can_add_stickies(self):
        # Setup
        u2 = UserFactory.create(is_superuser=True)
        # Run & check
        self.assertTrue(self.perm_handler.can_add_stickies(self.forum_1, u2))

    def test_knows_if_a_user_can_add_announces(self):
        # Setup
        u2 = UserFactory.create()
        assign_perm('can_post_announcements', self.u1, self.forum_1)
        # Run & check
        self.assertTrue(self.perm_handler.can_add_announcements(self.forum_1, self.u1))
        self.assertFalse(self.perm_handler.can_add_announcements(self.forum_1, u2))

    def test_knows_that_a_superuser_can_add_announces(self):
        # Setup
        u2 = UserFactory.create(is_superuser=True)
        # Run & check
        self.assertTrue(self.perm_handler.can_add_announcements(self.forum_1, u2))

    def test_knows_if_a_user_can_post_without_approval(self):
        # Setup
        u2 = UserFactory.create()
        assign_perm('can_post_without_approval', self.u1, self.forum_1)
        # Run & check
        self.assertTrue(self.perm_handler.can_post_without_approval(self.forum_1, self.u1))
        self.assertFalse(self.perm_handler.can_post_without_approval(self.forum_1, u2))

    def test_knows_that_a_superuser_can_post_without_approval(self):
        # Setup
        u2 = UserFactory.create(is_superuser=True)
        # Run & check
        self.assertTrue(self.perm_handler.can_post_without_approval(self.forum_1, u2))

    def test_knows_if_a_user_can_create_polls(self):
        # Setup
        u2 = UserFactory.create()
        assign_perm('can_create_poll', self.u1, self.forum_1)
        # Run & check
        self.assertTrue(self.perm_handler.can_create_polls(self.forum_1, self.u1))
        self.assertFalse(self.perm_handler.can_create_polls(self.forum_1, u2))

    def test_knows_that_a_superuser_can_create_polls(self):
        # Setup
        u2 = UserFactory.create(is_superuser=True)
        # Run & check
        self.assertTrue(self.perm_handler.can_create_polls(self.forum_1, u2))

    def test_knows_if_a_user_can_vote_in_polls(self):
        # Setup
        poll_1 = TopicPollFactory.create(topic=self.forum_1_topic)
        poll_2 = TopicPollFactory.create(topic=self.forum_3_topic)
        assign_perm('can_vote_in_polls', self.u1, self.forum_1)
        # Run & check
        self.assertTrue(self.perm_handler.can_vote_in_poll(poll_1, self.u1))
        self.assertFalse(self.perm_handler.can_vote_in_poll(poll_2, self.u1))

    def test_knows_that_a_superuser_can_vote_in_polls(self):
        # Setup
        poll = TopicPollFactory.create(topic=self.forum_1_topic)
        u2 = UserFactory.create(is_superuser=True)
        # Run & check
        self.assertTrue(self.perm_handler.can_vote_in_poll(poll, u2))

    def test_knows_that_a_user_should_no_vote_in_a_completed_poll(self):
        # Setup
        poll = TopicPollFactory.create(topic=self.forum_1_topic, duration=2)
        poll._meta.get_field_by_name('updated')[0].auto_now = False
        poll.created = datetime.datetime(2000, 1, 12)
        poll.save()
        poll._meta.get_field_by_name('updated')[0].auto_now = True
        assign_perm('can_vote_in_polls', self.u1, self.forum_1)
        # Run & check
        self.assertFalse(self.perm_handler.can_vote_in_poll(poll, self.u1))

    def test_knows_if_a_user_can_vote_again_in_a_poll(self):
        # Setup
        poll_1 = TopicPollFactory.create(topic=self.forum_1_topic, user_changes=True)
        poll_option_1 = TopicPollOptionFactory.create(poll=poll_1)
        TopicPollOptionFactory.create(poll=poll_1)

        poll_2 = TopicPollFactory.create(topic=self.forum_3_topic)
        poll_option_2 = TopicPollOptionFactory.create(poll=poll_2)
        TopicPollOptionFactory.create(poll=poll_2)

        TopicPollVoteFactory.create(poll_option=poll_option_1, voter=self.u1)
        TopicPollVoteFactory.create(poll_option=poll_option_2, voter=self.u1)

        assign_perm('can_vote_in_polls', self.u1, self.forum_1)
        assign_perm('can_vote_in_polls', self.u1, self.forum_3)
        # Run & check
        self.assertTrue(self.perm_handler.can_vote_in_poll(poll_1, self.u1))
        self.assertFalse(self.perm_handler.can_vote_in_poll(poll_2, self.u1))

    def test_knows_if_a_user_can_read_a_forum(self):
        # Setup
        u2 = UserFactory.create()
        # Run & check
        self.assertFalse(self.perm_handler.can_read_forum(self.forum_1, u2))
        self.assertTrue(self.perm_handler.can_read_forum(self.forum_3, self.u1))

    def test_knows_that_a_superuser_can_read_a_forum(self):
        # Setup
        u2 = UserFactory.create(is_superuser=True)
        # Run & check
        self.assertTrue(self.perm_handler.can_read_forum(self.forum_1, u2))
        self.assertTrue(self.perm_handler.can_read_forum(self.forum_3, u2))

    def test_knows_if_a_user_can_attach_files(self):
        # Setup
        u2 = UserFactory.create()
        assign_perm('can_attach_file', self.u1, self.forum_1)
        # Run & check
        self.assertTrue(self.perm_handler.can_attach_files(self.forum_1, self.u1))
        self.assertFalse(self.perm_handler.can_attach_files(self.forum_1, u2))

    def test_knows_that_a_superuser_can_attach_files(self):
        # Setup
        u2 = UserFactory.create(is_superuser=True)
        # Run & check
        self.assertTrue(self.perm_handler.can_attach_files(self.forum_1, u2))

    def test_knows_if_a_user_can_download_files(self):
        # Setup
        u2 = UserFactory.create()
        assign_perm('can_download_file', self.u1, self.forum_1)
        # Run & check
        self.assertTrue(self.perm_handler.can_download_files(self.forum_1, self.u1))
        self.assertFalse(self.perm_handler.can_download_files(self.forum_1, u2))

    def test_knows_that_a_superuser_can_download_files(self):
        # Setup
        u2 = UserFactory.create(is_superuser=True)
        # Run & check
        self.assertTrue(self.perm_handler.can_download_files(self.forum_1, u2))
