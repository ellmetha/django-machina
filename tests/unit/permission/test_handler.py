# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import datetime as dt

from django.contrib.auth.models import AnonymousUser
import pytest

from machina.core.db.models import get_model
from machina.core.loading import get_class
from machina.conf import settings as machina_settings
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

Forum = get_model('forum', 'Forum')
Post = get_model('forum_conversation', 'Post')
Topic = get_model('forum_conversation', 'Topic')

assign_perm = get_class('forum_permission.shortcuts', 'assign_perm')
remove_perm = get_class('forum_permission.shortcuts', 'remove_perm')

PermissionHandler = get_class('forum_permission.handler', 'PermissionHandler')


@pytest.mark.django_db
class TestPermissionHandler(object):
    @pytest.fixture(autouse=True)
    def setup(self):
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

        # Set up some topics
        self.forum_1_topic = create_topic(forum=self.forum_1, poster=self.u1)
        self.forum_3_topic = create_topic(forum=self.forum_3, poster=self.u1)
        self.forum_3_topic_2 = create_topic(
            forum=self.forum_3, poster=self.u1, status=Topic.TOPIC_LOCKED)

        # Set up some posts
        self.post_1 = PostFactory.create(topic=self.forum_1_topic, poster=self.u1)
        self.post_2 = PostFactory.create(topic=self.forum_3_topic, poster=self.u1)

        # Assign some permissions
        assign_perm('can_see_forum', self.u1, self.top_level_cat)
        assign_perm('can_see_forum', self.u1, self.forum_1)
        assign_perm('can_read_forum', self.g1, self.forum_3)

    def test_shows_a_forum_if_it_is_visible(self):
        # Setup
        u2 = UserFactory.create()
        u3 = AnonymousUser()
        assign_perm('can_see_forum', u2)  # Global user permission
        assign_perm('can_see_forum', u3)  # Global user permission
        forums = Forum.objects.filter(pk=self.top_level_cat.pk)
        # Run
        filtered_forums_1 = self.perm_handler.forum_list_filter(forums, self.u1)
        filtered_forums_2 = self.perm_handler.forum_list_filter(forums, u2)
        filtered_forums_3 = self.perm_handler.forum_list_filter(forums, u3)
        # Check
        assert set(filtered_forums_1) == set([self.top_level_cat, ])
        assert set(filtered_forums_2) == set([self.top_level_cat, ])
        assert set(filtered_forums_3) == set([self.top_level_cat, ])

    def test_hide_a_forum_if_it_is_not_visible(self):
        # Setup
        u2 = AnonymousUser()
        assign_perm('can_see_forum', u2, self.top_level_cat)
        forums = Forum.objects.filter(pk=self.top_level_cat.pk)
        # Run
        filtered_forums_1 = self.perm_handler.forum_list_filter(forums, self.u1)
        filtered_forums_2 = self.perm_handler.forum_list_filter(forums, u2)
        # Check
        assert set(filtered_forums_1) == set([self.top_level_cat, ])
        assert set(filtered_forums_2) == set([self.top_level_cat, ])

    def test_shows_a_forum_if_all_of_its_ancestors_are_visible(self):
        # Setup
        forums = Forum.objects.filter(parent=self.top_level_cat)
        # Run
        filtered_forums = self.perm_handler.forum_list_filter(forums, self.u1)
        # Check
        assert set(filtered_forums) == set([self.forum_1, self.forum_3])

    def test_hide_a_forum_if_one_of_its_ancestors_is_not_visible(self):
        # Setup
        remove_perm('can_see_forum', self.u1, self.top_level_cat)
        forums = Forum.objects.filter(parent=self.top_level_cat)
        # Run
        filtered_forums = self.perm_handler.forum_list_filter(forums, self.u1)
        # Check
        assert list(filtered_forums) == []

    def test_hide_a_top_level_forum_if_it_is_not_visible(self):
        # Setup
        remove_perm('can_see_forum', self.u1, self.top_level_cat)
        forums = Forum.objects.filter(id=self.top_level_cat.id)
        # Run
        filtered_forums = self.perm_handler.forum_list_filter(forums, self.u1)
        # Check
        assert list(filtered_forums) == []

    def test_knows_the_last_post_visible_inside_a_forum(self):
        # Run & check : no forum hidden
        last_post = self.perm_handler.get_forum_last_post(self.top_level_cat, self.u1)
        assert last_post == self.post_2

        # Run & check : one forum hidden
        self.perm_handler = PermissionHandler()
        remove_perm('can_read_forum', self.g1, self.forum_3)
        last_post = self.perm_handler.get_forum_last_post(self.top_level_cat, self.u1)
        assert last_post == self.post_1

        # Run & check : all forums hidden
        self.perm_handler = PermissionHandler()
        remove_perm('can_see_forum', self.u1, self.forum_1)
        last_post = self.perm_handler.get_forum_last_post(self.top_level_cat, self.u1)
        assert last_post is None

    def test_cannot_say_that_post_is_the_last_post_if_it_is_not_approved(self):
        # Setup
        PostFactory.create(topic=self.forum_1_topic, poster=self.u1, approved=False)
        remove_perm('can_read_forum', self.g1, self.forum_3)
        # Run
        last_post = self.perm_handler.get_forum_last_post(self.top_level_cat, self.u1)
        # Check
        assert last_post == self.post_1

    def test_shows_all_forums_to_a_superuser(self):
        # Setup
        u2 = UserFactory.create(is_superuser=True)
        forums = Forum.objects.filter(parent=self.top_level_cat)
        # Run
        filtered_forums = self.perm_handler.forum_list_filter(forums, u2)
        # Check
        assert set(filtered_forums) == set([self.forum_1, self.forum_2, self.forum_3])

    def test_knows_that_a_superuser_can_edit_all_posts(self):
        # Setup
        u2 = UserFactory.create(is_superuser=True)
        # Run & check
        assert self.perm_handler.can_edit_post(self.post_1, u2)

    def test_knows_if_an_owner_of_a_post_can_edit_it(self):
        # Setup
        u2 = UserFactory.create()
        assign_perm('can_edit_own_posts', self.u1, self.forum_1)
        assign_perm('can_edit_own_posts', u2, self.forum_1)
        # Run & check
        assert self.perm_handler.can_edit_post(self.post_1, self.u1)
        assert not self.perm_handler.can_edit_post(self.post_2, self.u1)
        assert not self.perm_handler.can_edit_post(self.post_1, u2)

    def test_knows_if_an_anonymous_owner_of_a_post_can_edit_it(self):
        # Setup
        u1 = AnonymousUser()
        u1.forum_key = '1234'
        u2 = AnonymousUser()
        u2.forum_key = '5678'
        u3 = AnonymousUser()
        u3.forum_key = None
        post_1 = PostFactory.create(topic=self.forum_1_topic, anonymous_key='1234')
        post_2 = PostFactory.create(topic=self.forum_3_topic, anonymous_key='1234')
        assign_perm('can_edit_own_posts', u1, self.forum_1)
        assign_perm('can_edit_own_posts', u2, self.forum_1)
        assign_perm('can_edit_own_posts', u3, self.forum_1)
        # Run & check
        assert self.perm_handler.can_edit_post(post_1, u1)
        assert not self.perm_handler.can_edit_post(post_2, u1)
        assert not self.perm_handler.can_edit_post(post_1, u2)
        assert not self.perm_handler.can_edit_post(post_1, u3)

    def test_knows_if_a_moderator_can_edit_a_post(self):
        # Setup
        moderator = UserFactory.create()
        assign_perm('can_edit_posts', moderator, self.forum_1)
        # Run & check
        assert self.perm_handler.can_edit_post(self.post_1, moderator)
        assert not self.perm_handler.can_edit_post(self.post_2, moderator)

    def test_knows_that_a_superuser_can_delete_all_posts(self):
        # Setup
        u2 = UserFactory.create(is_superuser=True)
        # Run & check
        assert self.perm_handler.can_delete_post(self.post_1, u2)

    def test_knows_if_an_owner_of_a_post_can_delete_it(self):
        # Setup
        u2 = UserFactory.create()
        assign_perm('can_delete_own_posts', self.u1, self.forum_1)
        assign_perm('can_delete_own_posts', u2, self.forum_1)
        # Run & check
        assert self.perm_handler.can_delete_post(self.post_1, self.u1)
        assert not self.perm_handler.can_delete_post(self.post_2, self.u1)
        assert not self.perm_handler.can_delete_post(self.post_1, u2)

    def test_knows_if_an_anonymous_owner_of_a_post_can_delete_it(self):
        # Setup
        u1 = AnonymousUser()
        u1.forum_key = '1234'
        u2 = AnonymousUser()
        u2.forum_key = '5678'
        u3 = AnonymousUser()
        u3.forum_key = None
        post_1 = PostFactory.create(topic=self.forum_1_topic, anonymous_key='1234')
        post_2 = PostFactory.create(topic=self.forum_3_topic, anonymous_key='1234')
        assign_perm('can_delete_own_posts', u1, self.forum_1)
        assign_perm('can_delete_own_posts', u2, self.forum_1)
        assign_perm('can_delete_own_posts', u3, self.forum_1)
        # Run & check
        assert self.perm_handler.can_delete_post(post_1, u1)
        assert not self.perm_handler.can_delete_post(post_2, u1)
        assert not self.perm_handler.can_delete_post(post_1, u2)
        assert not self.perm_handler.can_delete_post(post_1, u3)

    def test_knows_if_a_moderator_can_delete_a_post(self):
        # Setup
        moderator = UserFactory.create()
        assign_perm('can_delete_posts', moderator, self.forum_1)
        # Run & check
        assert self.perm_handler.can_delete_post(self.post_1, moderator)
        assert not self.perm_handler.can_delete_post(self.post_2, moderator)

    def test_knows_if_a_user_can_add_stickies(self):
        # Setup
        u2 = UserFactory.create()
        assign_perm('can_post_stickies', self.u1, self.forum_1)
        # Run & check
        assert self.perm_handler.can_add_stickies(self.forum_1, self.u1)
        assert not self.perm_handler.can_add_stickies(self.forum_1, u2)

    def test_knows_that_a_superuser_can_add_stickies(self):
        # Setup
        u2 = UserFactory.create(is_superuser=True)
        # Run & check
        assert self.perm_handler.can_add_stickies(self.forum_1, u2)

    def test_knows_if_a_user_can_add_announces(self):
        # Setup
        u2 = UserFactory.create()
        assign_perm('can_post_announcements', self.u1, self.forum_1)
        # Run & check
        assert self.perm_handler.can_add_announcements(self.forum_1, self.u1)
        assert not self.perm_handler.can_add_announcements(self.forum_1, u2)

    def test_knows_that_a_superuser_can_add_announces(self):
        # Setup
        u2 = UserFactory.create(is_superuser=True)
        # Run & check
        assert self.perm_handler.can_add_announcements(self.forum_1, u2)

    def test_knows_if_a_user_can_post_without_approval(self):
        # Setup
        u2 = UserFactory.create()
        assign_perm('can_post_without_approval', self.u1, self.forum_1)
        # Run & check
        assert self.perm_handler.can_post_without_approval(self.forum_1, self.u1)
        assert not self.perm_handler.can_post_without_approval(self.forum_1, u2)

    def test_knows_that_a_superuser_can_post_without_approval(self):
        # Setup
        u2 = UserFactory.create(is_superuser=True)
        # Run & check
        assert self.perm_handler.can_post_without_approval(self.forum_1, u2)

    def test_knows_if_a_user_can_add_posts_to_a_topic(self):
        # Setup
        u2 = UserFactory.create()
        assign_perm('can_reply_to_topics', self.u1, self.forum_1)
        # Run & check
        assert self.perm_handler.can_add_post(self.forum_1_topic, self.u1)
        assert not self.perm_handler.can_add_post(self.forum_1_topic, u2)

    def test_knows_that_a_superuser_can_add_posts_to_a_topic(self):
        # Setup
        u2 = UserFactory.create(is_superuser=True)
        # Run & check
        assert self.perm_handler.can_add_post(self.forum_1_topic, u2)

    def test_knows_that_a_user_cannot_add_posts_to_a_locked_topic(self):
        # Setup
        assign_perm('can_reply_to_topics', self.u1, self.forum_1)
        self.forum_1_topic.status = self.forum_1_topic.TOPIC_LOCKED
        self.forum_1_topic.save()
        # Run & check
        assert not self.perm_handler.can_add_post(self.forum_1_topic, self.u1)

    def test_knows_that_a_moderator_can_add_posts_to_a_locked_topic(self):
        # Setup
        assign_perm('can_reply_to_topics', self.u1, self.forum_1)
        assign_perm('can_reply_to_locked_topics', self.u1, self.forum_1)
        u2 = UserFactory.create()
        self.forum_1_topic.status = self.forum_1_topic.TOPIC_LOCKED
        self.forum_1_topic.save()
        # Run & check
        assert self.perm_handler.can_add_post(self.forum_1_topic, self.u1)
        assert not self.perm_handler.can_add_post(self.forum_1_topic, u2)

    def test_knows_if_a_user_can_create_polls(self):
        # Setup
        u2 = UserFactory.create()
        assign_perm('can_create_polls', self.u1, self.forum_1)
        # Run & check
        assert self.perm_handler.can_create_polls(self.forum_1, self.u1)
        assert not self.perm_handler.can_create_polls(self.forum_1, u2)

    def test_knows_that_a_superuser_can_create_polls(self):
        # Setup
        u2 = UserFactory.create(is_superuser=True)
        # Run & check
        assert self.perm_handler.can_create_polls(self.forum_1, u2)

    def test_knows_if_a_user_can_vote_in_polls(self):
        # Setup
        poll_1 = TopicPollFactory.create(topic=self.forum_1_topic)
        poll_2 = TopicPollFactory.create(topic=self.forum_3_topic)
        poll_3 = TopicPollFactory.create(topic=self.forum_3_topic_2)
        assign_perm('can_vote_in_polls', self.u1, self.forum_1)
        # Run & check
        assert self.perm_handler.can_vote_in_poll(poll_1, self.u1)
        assert not self.perm_handler.can_vote_in_poll(poll_2, self.u1)
        assert not self.perm_handler.can_vote_in_poll(poll_3, self.u1)

    def test_knows_if_an_anonymous_user_can_vote_in_polls(self):
        # Setup
        u3 = AnonymousUser()
        u3.forum_key = 1
        poll_1 = TopicPollFactory.create(topic=self.forum_1_topic)
        poll_2 = TopicPollFactory.create(topic=self.forum_3_topic)
        poll_3 = TopicPollFactory.create(topic=self.forum_3_topic_2)
        assign_perm('can_vote_in_polls', u3, self.forum_1)
        # Run & check
        assert self.perm_handler.can_vote_in_poll(poll_1, u3)
        assert not self.perm_handler.can_vote_in_poll(poll_2, u3)
        assert not self.perm_handler.can_vote_in_poll(poll_3, u3)

    def test_knows_that_an_anonymous_user_without_forum_key_cannot_vote_in_polls(self):
        # Setup
        u3 = AnonymousUser()
        poll_1 = TopicPollFactory.create(topic=self.forum_1_topic)
        poll_2 = TopicPollFactory.create(topic=self.forum_3_topic)
        poll_3 = TopicPollFactory.create(topic=self.forum_3_topic_2)
        assign_perm('can_vote_in_polls', u3, self.forum_1)
        # Run & check
        assert not self.perm_handler.can_vote_in_poll(poll_1, u3)
        assert not self.perm_handler.can_vote_in_poll(poll_2, u3)
        assert not self.perm_handler.can_vote_in_poll(poll_3, u3)

    def test_knows_that_a_superuser_can_vote_in_polls(self):
        # Setup
        poll = TopicPollFactory.create(topic=self.forum_1_topic)
        u2 = UserFactory.create(is_superuser=True)
        # Run & check
        assert self.perm_handler.can_vote_in_poll(poll, u2)

    def test_knows_that_a_user_should_no_vote_in_a_completed_poll(self):
        # Setup
        poll = TopicPollFactory.create(topic=self.forum_1_topic, duration=2)
        poll._meta.get_field_by_name('updated')[0].auto_now = False
        poll.created = dt.datetime(2000, 1, 12)
        poll.save()
        poll._meta.get_field_by_name('updated')[0].auto_now = True
        assign_perm('can_vote_in_polls', self.u1, self.forum_1)
        # Run & check
        assert not self.perm_handler.can_vote_in_poll(poll, self.u1)

    def test_knows_if_a_user_can_vote_again_in_a_poll(self):
        # Setup
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
        # Run & check
        assert self.perm_handler.can_vote_in_poll(poll_1, self.u1)
        assert not self.perm_handler.can_vote_in_poll(poll_2, self.u1)

    def test_knows_if_an_anonymous_user_can_vote_again_in_a_poll(self):
        # Setup
        u3 = AnonymousUser()
        u3.forum_key = 1
        poll_1 = TopicPollFactory.create(topic=self.forum_1_topic, user_changes=True)
        poll_option_1 = TopicPollOptionFactory.create(poll=poll_1)
        TopicPollOptionFactory.create(poll=poll_1)

        poll_2 = TopicPollFactory.create(topic=self.forum_3_topic)
        poll_option_2 = TopicPollOptionFactory.create(poll=poll_2)
        TopicPollOptionFactory.create(poll=poll_2)

        TopicPollVoteFactory.create(poll_option=poll_option_1, anonymous_key=1)
        TopicPollVoteFactory.create(poll_option=poll_option_2, anonymous_key=1)

        assign_perm('can_vote_in_polls', u3, self.forum_1)
        assign_perm('can_vote_in_polls', u3, self.forum_3)
        # Run & check
        assert self.perm_handler.can_vote_in_poll(poll_1, u3)
        assert not self.perm_handler.can_vote_in_poll(poll_2, u3)

    def test_knows_if_a_user_can_read_a_forum(self):
        # Setup
        u2 = UserFactory.create()
        # Run & check
        assert not self.perm_handler.can_read_forum(self.forum_1, u2)
        assert self.perm_handler.can_read_forum(self.forum_3, self.u1)

    def test_knows_that_a_superuser_can_read_a_forum(self):
        # Setup
        u2 = UserFactory.create(is_superuser=True)
        # Run & check
        assert self.perm_handler.can_read_forum(self.forum_1, u2)
        assert self.perm_handler.can_read_forum(self.forum_3, u2)

    def test_knows_if_a_user_can_attach_files(self):
        # Setup
        u2 = UserFactory.create()
        assign_perm('can_attach_file', self.u1, self.forum_1)
        # Run & check
        assert self.perm_handler.can_attach_files(self.forum_1, self.u1)
        assert not self.perm_handler.can_attach_files(self.forum_1, u2)

    def test_knows_that_a_superuser_can_attach_files(self):
        # Setup
        u2 = UserFactory.create(is_superuser=True)
        # Run & check
        assert self.perm_handler.can_attach_files(self.forum_1, u2)

    def test_knows_if_a_user_can_download_files(self):
        # Setup
        u2 = UserFactory.create()
        assign_perm('can_download_file', self.u1, self.forum_1)
        # Run & check
        assert self.perm_handler.can_download_files(self.forum_1, self.u1)
        assert not self.perm_handler.can_download_files(self.forum_1, u2)

    def test_knows_that_a_superuser_can_download_files(self):
        # Setup
        u2 = UserFactory.create(is_superuser=True)
        # Run & check
        assert self.perm_handler.can_download_files(self.forum_1, u2)

    def test_knows_the_list_of_forums_eligible_to_the_moderation_queue_for_a_given_user(self):
        # Setup
        u2 = UserFactory.create()
        assign_perm('can_approve_posts', self.u1, self.forum_1)
        # Run & check
        assert set(self.perm_handler.get_moderation_queue_forums(self.u1)) == set([self.forum_1, ])
        assert set(self.perm_handler.get_moderation_queue_forums(u2)) == set([])

    def test_knows_that_a_non_moderator_cannot_access_the_moderation_queue(self):
        # Setup
        u2 = UserFactory.create()
        # Run & check
        assert not self.perm_handler.can_access_moderation_queue(u2)

    def test_knows_that_a_moderator_can_access_the_moderation_queue(self):
        # Setup
        assign_perm('can_approve_posts', self.u1, self.forum_1)
        # Run & check
        assert self.perm_handler.can_access_moderation_queue(self.u1)

    def test_knows_that_a_superuser_can_access_the_moderation_queue(self):
        # Setup
        u2 = UserFactory.create(is_superuser=True)
        # Run & check
        assert self.perm_handler.can_access_moderation_queue(u2)

    def test_knows_if_a_user_can_lock_topics(self):
        # Setup
        u2 = UserFactory.create()
        assign_perm('can_lock_topics', self.u1, self.forum_1)
        # Run & check
        assert self.perm_handler.can_lock_topics(self.forum_1, self.u1)
        assert not self.perm_handler.can_lock_topics(self.forum_1, u2)

    def test_knows_that_a_superuser_can_lock_topics(self):
        # Setup
        u2 = UserFactory.create(is_superuser=True)
        # Run & check
        assert self.perm_handler.can_lock_topics(self.forum_1, u2)

    def test_knows_if_a_user_can_move_topics(self):
        # Setup
        u2 = UserFactory.create()
        assign_perm('can_move_topics', self.u1, self.forum_1)
        # Run & check
        assert self.perm_handler.can_move_topics(self.forum_1, self.u1)
        assert not self.perm_handler.can_move_topics(self.forum_1, u2)

    def test_knows_that_a_superuser_can_move_topics(self):
        # Setup
        u2 = UserFactory.create(is_superuser=True)
        # Run & check
        assert self.perm_handler.can_move_topics(self.forum_1, u2)

    def test_knows_the_forums_that_can_receive_moved_topics(self):
        # Setup
        assign_perm('can_move_topics', self.u1, self.forum_1)
        u2 = UserFactory.create(is_superuser=True)
        u3 = UserFactory.create()
        # Run & check
        assert set(self.perm_handler.get_target_forums_for_moved_topics(self.u1)) \
            == set([self.forum_1, ])
        assert set(self.perm_handler.get_target_forums_for_moved_topics(u2)) \
            == set(Forum.objects.filter(type=Forum.FORUM_POST))
        assert list(self.perm_handler.get_target_forums_for_moved_topics(u3)) == []

    def test_cannot_allow_forum_categories_to_receive_moved_topics(self):
        # Setup
        assign_perm('can_move_topics', self.u1, self.forum_1)
        assign_perm('can_move_topics', self.u1, self.top_level_cat)
        # Run & check
        assert set(self.perm_handler.get_target_forums_for_moved_topics(self.u1)) \
            == set([self.forum_1, ])

    def test_cannot_allow_forum_links_to_receive_moved_topics(self):
        # Setup
        assign_perm('can_move_topics', self.u1, self.forum_1)
        assign_perm('can_move_topics', self.u1, self.forum_3)
        # Run & check
        assert set(self.perm_handler.get_target_forums_for_moved_topics(self.u1)) \
            == set([self.forum_1, ])

    def test_knows_if_a_user_can_delete_topics(self):
        # Setup
        u2 = UserFactory.create()
        assign_perm('can_delete_posts', self.u1, self.forum_1)
        # Run & check
        assert self.perm_handler.can_delete_topics(self.forum_1, self.u1)
        assert not self.perm_handler.can_delete_topics(self.forum_1, u2)

    def test_knows_that_a_superuser_can_delete_topics(self):
        # Setup
        u2 = UserFactory.create(is_superuser=True)
        # Run & check
        assert self.perm_handler.can_delete_topics(self.forum_1, u2)

    def test_knows_if_a_user_can_update_topics_to_normal_topics(self):
        # Setup
        u2 = UserFactory.create()
        assign_perm('can_edit_posts', self.u1, self.forum_1)
        # Run & check
        assert self.perm_handler.can_update_topics_to_normal_topics(self.forum_1, self.u1)
        assert not self.perm_handler.can_update_topics_to_normal_topics(self.forum_1, u2)

    def test_knows_that_a_superuser_can_update_topics_to_normal_topics(self):
        # Setup
        u2 = UserFactory.create(is_superuser=True)
        # Run & check
        assert self.perm_handler.can_update_topics_to_normal_topics(self.forum_1, u2)

    def test_knows_if_a_user_can_update_topics_to_sticky_topics(self):
        # Setup
        u2 = UserFactory.create()
        assign_perm('can_edit_posts', self.u1, self.forum_1)
        assign_perm('can_post_stickies', self.u1, self.forum_1)
        # Run & check
        assert self.perm_handler.can_update_topics_to_sticky_topics(self.forum_1, self.u1)
        assert not self.perm_handler.can_update_topics_to_sticky_topics(self.forum_1, u2)

    def test_knows_that_a_superuser_can_update_topics_to_sticky_topics(self):
        # Setup
        u2 = UserFactory.create(is_superuser=True)
        # Run & check
        assert self.perm_handler.can_update_topics_to_sticky_topics(self.forum_1, u2)

    def test_knows_if_a_user_can_update_topics_to_announces(self):
        # Setup
        u2 = UserFactory.create()
        assign_perm('can_edit_posts', self.u1, self.forum_1)
        assign_perm('can_post_announcements', self.u1, self.forum_1)
        # Run & check
        assert self.perm_handler.can_update_topics_to_announces(self.forum_1, self.u1)
        assert not self.perm_handler.can_update_topics_to_announces(self.forum_1, u2)

    def test_knows_that_a_superuser_can_update_topics_to_announces(self):
        # Setup
        u2 = UserFactory.create(is_superuser=True)
        # Run & check
        assert self.perm_handler.can_update_topics_to_announces(self.forum_1, u2)

    def test_knows_if_a_user_can_approve_posts(self):
        # Setup
        u2 = UserFactory.create()
        assign_perm('can_approve_posts', self.u1, self.forum_1)
        # Run & check
        assert self.perm_handler.can_approve_posts(self.forum_1, self.u1)
        assert not self.perm_handler.can_approve_posts(self.forum_1, u2)

    def test_knows_that_a_superuser_can_approve_posts(self):
        # Setup
        u2 = UserFactory.create(is_superuser=True)
        # Run & check
        assert self.perm_handler.can_approve_posts(self.forum_1, u2)

    def test_filter_methods_fallback_to_default_forum_permissions_if_applicable(self):
        # Setup
        codenames = [
            'can_vote_in_polls',
            'can_add_announcements',
        ]
        machina_settings.DEFAULT_AUTHENTICATED_USER_FORUM_PERMISSIONS = codenames
        # Run & check
        assert set(self.perm_handler._get_forums_for_user(self.u1, codenames)) \
            == set(Forum.objects.all())
        machina_settings.DEFAULT_AUTHENTICATED_USER_FORUM_PERMISSIONS = []

    def test_knows_if_a_user_can_subscribe_to_topics(self):
        # Setup
        u2 = UserFactory.create()
        assign_perm('can_read_forum', self.u1, self.forum_1)
        # Run & check
        assert self.perm_handler.can_subscribe_to_topic(self.forum_1_topic, self.u1)
        assert not self.perm_handler.can_subscribe_to_topic(self.forum_1_topic, u2)

    def test_knows_that_a_superuser_can_subscribe_to_topics(self):
        # Setup
        u2 = UserFactory.create(is_superuser=True)
        # Run & check
        assert self.perm_handler.can_subscribe_to_topic(self.forum_1_topic, u2)

    def test_knows_that_an_anonymous_user_cannot_subscribe_to_topics(self):
        # Setup
        u2 = AnonymousUser()
        assign_perm('can_read_forum', u2, self.forum_1)
        # Run & check
        assert not self.perm_handler.can_subscribe_to_topic(self.forum_1_topic, u2)

    def test_knows_if_a_user_can_unsubscribe_from_topics(self):
        # Setup
        self.forum_1_topic.subscribers.add(self.u1)
        u2 = UserFactory.create()
        assign_perm('can_read_forum', self.u1, self.forum_1)
        # Run & check
        assert self.perm_handler.can_unsubscribe_from_topic(self.forum_1_topic, self.u1)
        assert not self.perm_handler.can_unsubscribe_from_topic(self.forum_1_topic, u2)

    def test_knows_that_a_superuser_can_unsubscribe_from_topics(self):
        # Setup
        u2 = UserFactory.create(is_superuser=True)
        self.forum_1_topic.subscribers.add(u2)
        # Run & check
        assert self.perm_handler.can_unsubscribe_from_topic(self.forum_1_topic, u2)

    def test_knows_that_an_anonymous_user_cannot_unsubscribe_from_topics(self):
        # Setup
        u2 = AnonymousUser()
        assign_perm('can_read_forum', u2, self.forum_1)
        # Run & check
        assert not self.perm_handler.can_unsubscribe_from_topic(self.forum_1_topic, u2)
