# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from faker import Factory as FakerFactory
import pytest

from machina.core.loading import get_class
from machina.core.db.models import get_model
from machina.test.factories import create_forum
from machina.test.factories import create_topic
from machina.test.factories import ForumReadTrackFactory
from machina.test.factories import PostFactory
from machina.test.factories import TopicPollFactory
from machina.test.factories import TopicPollOptionFactory
from machina.test.testcases import BaseClientTestCase

faker = FakerFactory.create()

ForumReadTrack = get_model('forum_tracking', 'ForumReadTrack')
Post = get_model('forum_conversation', 'Post')
Topic = get_model('forum_conversation', 'Topic')
TopicReadTrack = get_model('forum_tracking', 'TopicReadTrack')

PermissionHandler = get_class('forum_permission.handler', 'PermissionHandler')
assign_perm = get_class('forum_permission.shortcuts', 'assign_perm')
remove_perm = get_class('forum_permission.shortcuts', 'remove_perm')


class TestTopicLockView(BaseClientTestCase):
    @pytest.fixture(autouse=True)
    def setup(self):
        # Permission handler
        self.perm_handler = PermissionHandler()

        # Set up a top-level forum
        self.top_level_forum = create_forum()

        # Set up a topic and some posts
        self.topic = create_topic(forum=self.top_level_forum, poster=self.user)
        self.first_post = PostFactory.create(topic=self.topic, poster=self.user)
        self.post = PostFactory.create(topic=self.topic, poster=self.user)

        # Mark the forum as read
        ForumReadTrackFactory.create(forum=self.top_level_forum, user=self.user)

        # Assign some permissions
        assign_perm('can_read_forum', self.user, self.top_level_forum)
        assign_perm('can_reply_to_topics', self.user, self.top_level_forum)
        assign_perm('can_edit_own_posts', self.user, self.top_level_forum)
        assign_perm('can_delete_own_posts', self.user, self.top_level_forum)
        assign_perm('can_lock_topics', self.user, self.top_level_forum)

    def test_browsing_works(self):
        # Setup
        correct_url = reverse(
            'forum_moderation:topic_lock',
            kwargs={'slug': self.topic.slug, 'pk': self.topic.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        assert response.status_code == 200

    def test_can_lock_topics(self):
        # Setup
        correct_url = reverse(
            'forum_moderation:topic_lock',
            kwargs={'slug': self.topic.slug, 'pk': self.topic.pk})
        # Run
        self.client.post(correct_url, follow=True)
        # Check
        self.topic.refresh_from_db()
        assert self.topic.is_locked

    def test_redirects_to_the_topic_view(self):
        # Setup
        correct_url = reverse(
            'forum_moderation:topic_lock',
            kwargs={'slug': self.topic.slug, 'pk': self.topic.pk})
        # Run
        response = self.client.post(correct_url, follow=True)
        # Check
        topic_url = reverse(
            'forum_conversation:topic',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'slug': self.topic.slug, 'pk': self.topic.pk})
        assert len(response.redirect_chain)
        last_url, status_code = response.redirect_chain[-1]
        assert topic_url in last_url

    def test_cannot_be_browsed_by_users_who_cannot_lock_topics(self):
        # Setup
        remove_perm('can_lock_topics', self.user, self.top_level_forum)
        correct_url = reverse(
            'forum_moderation:topic_lock',
            kwargs={'slug': self.topic.slug, 'pk': self.topic.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        assert response.status_code == 403


class TestTopicUnlockView(BaseClientTestCase):
    @pytest.fixture(autouse=True)
    def setup(self):
        # Permission handler
        self.perm_handler = PermissionHandler()

        # Set up a top-level forum
        self.top_level_forum = create_forum()

        # Set up a topic and some posts
        self.topic = create_topic(
            forum=self.top_level_forum, poster=self.user,
            status=Topic.TOPIC_LOCKED)
        self.first_post = PostFactory.create(topic=self.topic, poster=self.user)
        self.post = PostFactory.create(topic=self.topic, poster=self.user)

        # Mark the forum as read
        ForumReadTrackFactory.create(forum=self.top_level_forum, user=self.user)

        # Assign some permissions
        assign_perm('can_read_forum', self.user, self.top_level_forum)
        assign_perm('can_reply_to_topics', self.user, self.top_level_forum)
        assign_perm('can_edit_own_posts', self.user, self.top_level_forum)
        assign_perm('can_delete_own_posts', self.user, self.top_level_forum)
        assign_perm('can_lock_topics', self.user, self.top_level_forum)

    def test_browsing_works(self):
        # Setup
        correct_url = reverse(
            'forum_moderation:topic_unlock',
            kwargs={'slug': self.topic.slug, 'pk': self.topic.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        assert response.status_code == 200

    def test_can_unlock_topics(self):
        # Setup
        correct_url = reverse(
            'forum_moderation:topic_unlock',
            kwargs={'slug': self.topic.slug, 'pk': self.topic.pk})
        # Run
        self.client.post(correct_url, follow=True)
        # Check
        self.topic.refresh_from_db()
        assert not self.topic.is_locked

    def test_redirects_to_the_topic_view(self):
        # Setup
        correct_url = reverse(
            'forum_moderation:topic_unlock',
            kwargs={'slug': self.topic.slug, 'pk': self.topic.pk})
        # Run
        response = self.client.post(correct_url, follow=True)
        # Check
        topic_url = reverse(
            'forum_conversation:topic',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'slug': self.topic.slug, 'pk': self.topic.pk})
        assert len(response.redirect_chain)
        last_url, status_code = response.redirect_chain[-1]
        assert topic_url in last_url

    def test_cannot_be_browsed_by_users_who_cannot_unlock_topics(self):
        # Setup
        remove_perm('can_lock_topics', self.user, self.top_level_forum)
        correct_url = reverse(
            'forum_moderation:topic_unlock',
            kwargs={'slug': self.topic.slug, 'pk': self.topic.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        assert response.status_code == 403


class TestTopicDeleteView(BaseClientTestCase):
    @pytest.fixture(autouse=True)
    def setup(self):
        # Permission handler
        self.perm_handler = PermissionHandler()

        # Set up a top-level forum
        self.top_level_forum = create_forum()

        # Set up a topic and some posts
        self.topic = create_topic(forum=self.top_level_forum, poster=self.user)
        self.first_post = PostFactory.create(topic=self.topic, poster=self.user)
        self.post = PostFactory.create(topic=self.topic, poster=self.user)

        # Mark the forum as read
        ForumReadTrackFactory.create(forum=self.top_level_forum, user=self.user)

        # Assign some permissions
        assign_perm('can_read_forum', self.user, self.top_level_forum)
        assign_perm('can_reply_to_topics', self.user, self.top_level_forum)
        assign_perm('can_edit_own_posts', self.user, self.top_level_forum)
        assign_perm('can_delete_own_posts', self.user, self.top_level_forum)
        assign_perm('can_delete_posts', self.user, self.top_level_forum)

    def test_browsing_works(self):
        # Setup
        correct_url = reverse(
            'forum_moderation:topic_delete',
            kwargs={'slug': self.topic.slug, 'pk': self.topic.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        assert response.status_code == 200

    def test_can_delete_topics(self):
        # Setup
        correct_url = reverse(
            'forum_moderation:topic_delete',
            kwargs={'slug': self.topic.slug, 'pk': self.topic.pk})
        # Run
        self.client.post(correct_url, follow=True)
        # Check
        with pytest.raises(ObjectDoesNotExist):
            topic = Topic.objects.get(pk=self.topic.pk)  # noqa

    def test_redirects_to_the_forum_view(self):
        # Setup
        correct_url = reverse(
            'forum_moderation:topic_delete',
            kwargs={'slug': self.topic.slug, 'pk': self.topic.pk})
        # Run
        response = self.client.post(correct_url, follow=True)
        # Check
        forum_url = reverse(
            'forum:forum',
            kwargs={'slug': self.top_level_forum.slug, 'pk': self.top_level_forum.pk})
        assert len(response.redirect_chain)
        last_url, status_code = response.redirect_chain[-1]
        assert forum_url in last_url

    def test_cannot_be_browsed_by_users_who_cannot_delete_topics(self):
        # Setup
        remove_perm('can_delete_posts', self.user, self.top_level_forum)
        correct_url = reverse(
            'forum_moderation:topic_delete',
            kwargs={'slug': self.topic.slug, 'pk': self.topic.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        assert response.status_code == 403


class TestTopicMoveView(BaseClientTestCase):
    @pytest.fixture(autouse=True)
    def setup(self):
        # Permission handler
        self.perm_handler = PermissionHandler()

        # Set up a top-level forum
        self.top_level_forum = create_forum()
        self.other_forum = create_forum()

        # Set up a topic and some posts
        self.topic = create_topic(forum=self.top_level_forum, poster=self.user)
        self.first_post = PostFactory.create(topic=self.topic, poster=self.user)
        self.post = PostFactory.create(topic=self.topic, poster=self.user)

        # Mark the forum as read
        ForumReadTrackFactory.create(forum=self.top_level_forum, user=self.user)

        # Assign some permissions
        assign_perm('can_read_forum', self.user, self.top_level_forum)
        assign_perm('can_reply_to_topics', self.user, self.top_level_forum)
        assign_perm('can_edit_own_posts', self.user, self.top_level_forum)
        assign_perm('can_delete_own_posts', self.user, self.top_level_forum)
        assign_perm('can_move_topics', self.user, self.top_level_forum)
        assign_perm('can_move_topics', self.user, self.other_forum)

    def test_browsing_works(self):
        # Setup
        correct_url = reverse(
            'forum_moderation:topic_move',
            kwargs={'slug': self.topic.slug, 'pk': self.topic.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        assert response.status_code == 200

    def test_can_move_topics(self):
        # Setup
        correct_url = reverse(
            'forum_moderation:topic_move',
            kwargs={'slug': self.topic.slug, 'pk': self.topic.pk})
        post_data = {
            'forum': self.other_forum.id,
        }
        # Run
        self.client.post(correct_url, post_data, follow=True)
        # Check
        self.topic.refresh_from_db()
        assert self.topic.forum == self.other_forum

    def test_can_move_and_lock_topics(self):
        # Setup
        correct_url = reverse(
            'forum_moderation:topic_move',
            kwargs={'slug': self.topic.slug, 'pk': self.topic.pk})
        post_data = {
            'forum': self.other_forum.id,
            'lock_topic': True,
        }
        # Run
        self.client.post(correct_url, post_data, follow=True)
        # Check
        self.topic.refresh_from_db()
        assert self.topic.forum == self.other_forum
        assert self.topic.is_locked

    def test_can_move_and_unlock_a_topic_if_it_was_locked(self):
        # Setup
        self.topic.status = self.topic.TOPIC_LOCKED
        self.topic.save()
        correct_url = reverse(
            'forum_moderation:topic_move',
            kwargs={'slug': self.topic.slug, 'pk': self.topic.pk})
        post_data = {
            'forum': self.other_forum.id,
            'lock_topic': False,
        }
        # Run
        self.client.post(correct_url, post_data, follow=True)
        # Check
        self.topic.refresh_from_db()
        assert self.topic.forum == self.other_forum
        assert not self.topic.is_locked

    def test_cannot_be_browsed_by_users_who_cannot_move_topics(self):
        # Setup
        remove_perm('can_move_topics', self.user, self.top_level_forum)
        correct_url = reverse(
            'forum_moderation:topic_move',
            kwargs={'slug': self.topic.slug, 'pk': self.topic.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        assert response.status_code == 403


class TestTopicUpdateToNormalTopicView(BaseClientTestCase):
    @pytest.fixture(autouse=True)
    def setup(self):
        # Permission handler
        self.perm_handler = PermissionHandler()

        # Set up a top-level forum
        self.top_level_forum = create_forum()

        # Set up a topic and some posts
        self.topic = create_topic(
            forum=self.top_level_forum, poster=self.user,
            type=Topic.TOPIC_POST,
            status=Topic.TOPIC_LOCKED)
        self.first_post = PostFactory.create(topic=self.topic, poster=self.user)
        self.post = PostFactory.create(topic=self.topic, poster=self.user)

        # Mark the forum as read
        ForumReadTrackFactory.create(forum=self.top_level_forum, user=self.user)

        # Assign some permissions
        assign_perm('can_read_forum', self.user, self.top_level_forum)
        assign_perm('can_reply_to_topics', self.user, self.top_level_forum)
        assign_perm('can_edit_own_posts', self.user, self.top_level_forum)
        assign_perm('can_delete_own_posts', self.user, self.top_level_forum)
        assign_perm('can_edit_posts', self.user, self.top_level_forum)

    def test_browsing_works(self):
        # Setup
        correct_url = reverse(
            'forum_moderation:topic_update_to_post',
            kwargs={'slug': self.topic.slug, 'pk': self.topic.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        assert response.status_code == 200

    def test_can_update_topics_to_standard_topics(self):
        # Setup
        correct_url = reverse(
            'forum_moderation:topic_update_to_post',
            kwargs={'slug': self.topic.slug, 'pk': self.topic.pk})
        # Run
        self.client.post(correct_url, follow=True)
        # Check
        self.topic.refresh_from_db()
        assert self.topic.is_topic

    def test_redirects_to_the_topic_view(self):
        # Setup
        correct_url = reverse(
            'forum_moderation:topic_update_to_post',
            kwargs={'slug': self.topic.slug, 'pk': self.topic.pk})
        # Run
        response = self.client.post(correct_url, follow=True)
        # Check
        topic_url = reverse(
            'forum_conversation:topic',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'slug': self.topic.slug, 'pk': self.topic.pk})
        assert len(response.redirect_chain)
        last_url, status_code = response.redirect_chain[-1]
        assert topic_url in last_url

    def test_cannot_be_browsed_by_users_who_cannot_update_topics_to_normal_topics(self):
        # Setup
        remove_perm('can_edit_posts', self.user, self.top_level_forum)
        correct_url = reverse(
            'forum_moderation:topic_update_to_post',
            kwargs={'slug': self.topic.slug, 'pk': self.topic.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        assert response.status_code == 403


class TestTopicUpdateToStickyTopicView(BaseClientTestCase):
    @pytest.fixture(autouse=True)
    def setup(self):
        # Permission handler
        self.perm_handler = PermissionHandler()

        # Set up a top-level forum
        self.top_level_forum = create_forum()

        # Set up a topic and some posts
        self.topic = create_topic(
            forum=self.top_level_forum, poster=self.user,
            status=Topic.TOPIC_LOCKED)
        self.first_post = PostFactory.create(topic=self.topic, poster=self.user)
        self.post = PostFactory.create(topic=self.topic, poster=self.user)

        # Mark the forum as read
        ForumReadTrackFactory.create(forum=self.top_level_forum, user=self.user)

        # Assign some permissions
        assign_perm('can_read_forum', self.user, self.top_level_forum)
        assign_perm('can_reply_to_topics', self.user, self.top_level_forum)
        assign_perm('can_edit_own_posts', self.user, self.top_level_forum)
        assign_perm('can_delete_own_posts', self.user, self.top_level_forum)
        assign_perm('can_edit_posts', self.user, self.top_level_forum)
        assign_perm('can_post_stickies', self.user, self.top_level_forum)

    def test_browsing_works(self):
        # Setup
        correct_url = reverse(
            'forum_moderation:topic_update_to_sticky',
            kwargs={'slug': self.topic.slug, 'pk': self.topic.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        assert response.status_code == 200

    def test_can_update_topics_to_sticky_topics(self):
        # Setup
        correct_url = reverse(
            'forum_moderation:topic_update_to_sticky',
            kwargs={'slug': self.topic.slug, 'pk': self.topic.pk})
        # Run
        self.client.post(correct_url, follow=True)
        # Check
        self.topic.refresh_from_db()
        assert self.topic.is_sticky

    def test_redirects_to_the_topic_view(self):
        # Setup
        correct_url = reverse(
            'forum_moderation:topic_update_to_sticky',
            kwargs={'slug': self.topic.slug, 'pk': self.topic.pk})
        # Run
        response = self.client.post(correct_url, follow=True)
        # Check
        topic_url = reverse(
            'forum_conversation:topic',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'slug': self.topic.slug, 'pk': self.topic.pk})
        assert len(response.redirect_chain)
        last_url, status_code = response.redirect_chain[-1]
        assert topic_url in last_url

    def test_cannot_be_browsed_by_users_who_cannot_update_topics_to_sticky_topics(self):
        # Setup
        remove_perm('can_post_stickies', self.user, self.top_level_forum)
        correct_url = reverse(
            'forum_moderation:topic_update_to_sticky',
            kwargs={'slug': self.topic.slug, 'pk': self.topic.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        assert response.status_code == 403


class TestTopicUpdateToAnnounceView(BaseClientTestCase):
    @pytest.fixture(autouse=True)
    def setup(self):
        # Permission handler
        self.perm_handler = PermissionHandler()

        # Set up a top-level forum
        self.top_level_forum = create_forum()

        # Set up a topic and some posts
        self.topic = create_topic(
            forum=self.top_level_forum, poster=self.user,
            status=Topic.TOPIC_LOCKED)
        self.first_post = PostFactory.create(topic=self.topic, poster=self.user)
        self.post = PostFactory.create(topic=self.topic, poster=self.user)

        # Mark the forum as read
        ForumReadTrackFactory.create(forum=self.top_level_forum, user=self.user)

        # Assign some permissions
        assign_perm('can_read_forum', self.user, self.top_level_forum)
        assign_perm('can_reply_to_topics', self.user, self.top_level_forum)
        assign_perm('can_edit_own_posts', self.user, self.top_level_forum)
        assign_perm('can_delete_own_posts', self.user, self.top_level_forum)
        assign_perm('can_edit_posts', self.user, self.top_level_forum)
        assign_perm('can_post_announcements', self.user, self.top_level_forum)

    def test_browsing_works(self):
        # Setup
        correct_url = reverse(
            'forum_moderation:topic_update_to_announce',
            kwargs={'slug': self.topic.slug, 'pk': self.topic.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        assert response.status_code == 200

    def test_can_update_topics_to_sticky_topics(self):
        # Setup
        correct_url = reverse(
            'forum_moderation:topic_update_to_announce',
            kwargs={'slug': self.topic.slug, 'pk': self.topic.pk})
        # Run
        self.client.post(correct_url, follow=True)
        # Check
        self.topic.refresh_from_db()
        assert self.topic.is_announce

    def test_redirects_to_the_topic_view(self):
        # Setup
        correct_url = reverse(
            'forum_moderation:topic_update_to_announce',
            kwargs={'slug': self.topic.slug, 'pk': self.topic.pk})
        # Run
        response = self.client.post(correct_url, follow=True)
        # Check
        topic_url = reverse(
            'forum_conversation:topic',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'slug': self.topic.slug, 'pk': self.topic.pk})
        assert len(response.redirect_chain)
        last_url, status_code = response.redirect_chain[-1]
        assert topic_url in last_url

    def test_cannot_be_browsed_by_users_who_cannot_update_topics_to_announces(self):
        # Setup
        remove_perm('can_post_announcements', self.user, self.top_level_forum)
        correct_url = reverse(
            'forum_moderation:topic_update_to_announce',
            kwargs={'slug': self.topic.slug, 'pk': self.topic.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        assert response.status_code == 403


class TestModerationQueueListView(BaseClientTestCase):
    @pytest.fixture(autouse=True)
    def setup(self):
        # Permission handler
        self.perm_handler = PermissionHandler()

        # Set up a top-level forum
        self.top_level_forum = create_forum()

        # Set up a topic and some posts
        self.topic = create_topic(
            forum=self.top_level_forum, poster=self.user,
            status=Topic.TOPIC_LOCKED)
        self.first_post = PostFactory.create(topic=self.topic, poster=self.user)
        self.post = PostFactory.create(topic=self.topic, poster=self.user)

        # Mark the forum as read
        ForumReadTrackFactory.create(forum=self.top_level_forum, user=self.user)

        # Assign some permissions
        assign_perm('can_read_forum', self.user, self.top_level_forum)
        assign_perm('can_approve_posts', self.user, self.top_level_forum)

    def test_browsing_works(self):
        # Setup
        correct_url = reverse(
            'forum_moderation:queue')
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        assert response.status_code == 200

    def test_cannot_be_browsed_by_users_who_cannot_approve_posts(self):
        # Setup
        remove_perm('can_approve_posts', self.user, self.top_level_forum)
        correct_url = reverse(
            'forum_moderation:queue')
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        assert response.status_code == 403

    def test_displays_only_non_approved_posts(self):
        # Setup
        post2 = PostFactory.create(topic=self.topic, poster=self.user, approved=False)
        correct_url = reverse(
            'forum_moderation:queue')
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        assert response.status_code == 200
        assert set(response.context_data['posts']) == set([post2, ])

    def test_display_only_posts_whose_forums_are_eligible_to_the_moderation_queue_for_the_given_user(self):  # noqa
        # Setup
        post2 = PostFactory.create(topic=self.topic, poster=self.user, approved=False)
        f1 = create_forum()
        topic = create_topic(
            forum=f1, poster=self.user)
        PostFactory.create(topic=topic, poster=self.user, approved=False)
        correct_url = reverse(
            'forum_moderation:queue')
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        assert response.status_code == 200
        assert set(response.context_data['posts']) == set([post2, ])


class TestModerationQueueDetailView(BaseClientTestCase):
    @pytest.fixture(autouse=True)
    def setup(self):
        # Permission handler
        self.perm_handler = PermissionHandler()

        # Set up a top-level forum
        self.top_level_forum = create_forum()

        # Set up a topic and some posts
        self.topic = create_topic(
            forum=self.top_level_forum, poster=self.user,
            status=Topic.TOPIC_LOCKED)
        self.first_post = PostFactory.create(topic=self.topic, poster=self.user)
        self.post = PostFactory.create(topic=self.topic, poster=self.user, approved=False)

        # Mark the forum as read
        ForumReadTrackFactory.create(forum=self.top_level_forum, user=self.user)

        # Assign some permissions
        assign_perm('can_approve_posts', self.user, self.top_level_forum)

    def test_browsing_works(self):
        # Setup
        correct_url = reverse(
            'forum_moderation:queued_post', kwargs={'pk': self.post.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        assert response.status_code == 200

    def test_cannot_be_browsed_by_users_who_cannot_approve_posts(self):
        # Setup
        remove_perm('can_approve_posts', self.user, self.top_level_forum)
        correct_url = reverse(
            'forum_moderation:queued_post', kwargs={'pk': self.post.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        assert response.status_code == 403

    def test_inserts_the_topic_poll_in_the_context_if_applicable(self):
        # Setup
        poll = TopicPollFactory.create(topic=self.topic)
        option_1 = TopicPollOptionFactory.create(poll=poll)
        option_2 = TopicPollOptionFactory.create(poll=poll)
        correct_url = reverse(
            'forum_moderation:queued_post', kwargs={'pk': self.post.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        assert response.status_code == 200
        assert response.context['poll'] == poll
        assert set(response.context['poll_options']) == set({option_1, option_2, })


class TestPostApproveView(BaseClientTestCase):
    @pytest.fixture(autouse=True)
    def setup(self):
        # Permission handler
        self.perm_handler = PermissionHandler()

        # Set up a top-level forum
        self.top_level_forum = create_forum()

        # Set up a topic and some posts
        self.topic = create_topic(
            forum=self.top_level_forum, poster=self.user,
            status=Topic.TOPIC_LOCKED)
        self.first_post = PostFactory.create(topic=self.topic, poster=self.user)
        self.post = PostFactory.create(topic=self.topic, poster=self.user, approved=False)

        # Mark the forum as read
        ForumReadTrackFactory.create(forum=self.top_level_forum, user=self.user)

        # Assign some permissions
        assign_perm('can_approve_posts', self.user, self.top_level_forum)

    def test_browsing_works(self):
        # Setup
        correct_url = reverse(
            'forum_moderation:approve_queued_post',
            kwargs={'pk': self.post.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        assert response.status_code == 200

    def test_can_approve_posts(self):
        # Setup
        correct_url = reverse(
            'forum_moderation:approve_queued_post',
            kwargs={'pk': self.post.pk})
        # Run
        self.client.post(correct_url, follow=True)
        # Check
        self.post.refresh_from_db()
        assert self.post.approved

    def test_redirects_to_the_moderation_queue(self):
        # Setup
        correct_url = reverse(
            'forum_moderation:approve_queued_post',
            kwargs={'pk': self.post.pk})
        # Run
        response = self.client.post(correct_url, follow=True)
        # Check
        moderation_queue_url = reverse('forum_moderation:queue')
        assert len(response.redirect_chain)
        last_url, status_code = response.redirect_chain[-1]
        assert moderation_queue_url in last_url

    def test_cannot_be_browsed_by_users_who_cannot_approve_posts(self):
        # Setup
        remove_perm('can_approve_posts', self.user, self.top_level_forum)
        correct_url = reverse(
            'forum_moderation:approve_queued_post',
            kwargs={'pk': self.post.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        assert response.status_code == 403


class TestPostDisapproveView(BaseClientTestCase):
    @pytest.fixture(autouse=True)
    def setup(self):
        # Permission handler
        self.perm_handler = PermissionHandler()

        # Set up a top-level forum
        self.top_level_forum = create_forum()

        # Set up a topic and some posts
        self.topic = create_topic(
            forum=self.top_level_forum, poster=self.user,
            status=Topic.TOPIC_LOCKED)
        self.first_post = PostFactory.create(topic=self.topic, poster=self.user)
        self.post = PostFactory.create(topic=self.topic, poster=self.user, approved=False)

        # Mark the forum as read
        ForumReadTrackFactory.create(forum=self.top_level_forum, user=self.user)

        # Assign some permissions
        assign_perm('can_approve_posts', self.user, self.top_level_forum)

    def test_browsing_works(self):
        # Setup
        correct_url = reverse(
            'forum_moderation:disapprove_queued_post',
            kwargs={'pk': self.post.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        assert response.status_code == 200

    def test_can_disapprove_posts(self):
        # Setup
        old_post_pk = self.post.pk
        correct_url = reverse(
            'forum_moderation:disapprove_queued_post',
            kwargs={'pk': self.post.pk})
        # Run
        self.client.post(correct_url, follow=True)
        # Check
        with pytest.raises(ObjectDoesNotExist):
            Post.objects.get(pk=old_post_pk)

    def test_redirects_to_the_moderation_queue(self):
        # Setup
        correct_url = reverse(
            'forum_moderation:disapprove_queued_post',
            kwargs={'pk': self.post.pk})
        # Run
        response = self.client.post(correct_url, follow=True)
        # Check
        moderation_queue_url = reverse('forum_moderation:queue')
        assert len(response.redirect_chain)
        last_url, status_code = response.redirect_chain[-1]
        assert moderation_queue_url in last_url

    def test_cannot_be_browsed_by_users_who_cannot_approve_posts(self):
        # Setup
        remove_perm('can_approve_posts', self.user, self.top_level_forum)
        correct_url = reverse(
            'forum_moderation:disapprove_queued_post',
            kwargs={'pk': self.post.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        assert response.status_code == 403
