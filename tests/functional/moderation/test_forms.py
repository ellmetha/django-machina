# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from faker import Factory as FakerFactory
import pytest

from machina.apps.forum_moderation.forms import TopicMoveForm
from machina.core.loading import get_class
from machina.core.db.models import get_model
from machina.test.factories import create_category_forum
from machina.test.factories import create_forum
from machina.test.factories import create_link_forum
from machina.test.factories import create_topic
from machina.test.factories import ForumReadTrackFactory
from machina.test.factories import PostFactory
from machina.test.factories import UserFactory

faker = FakerFactory.create()

ForumReadTrack = get_model('forum_tracking', 'ForumReadTrack')
Post = get_model('forum_conversation', 'Post')
Topic = get_model('forum_conversation', 'Topic')
TopicReadTrack = get_model('forum_tracking', 'TopicReadTrack')

PermissionHandler = get_class('forum_permission.handler', 'PermissionHandler')
assign_perm = get_class('forum_permission.shortcuts', 'assign_perm')
remove_perm = get_class('forum_permission.shortcuts', 'remove_perm')


@pytest.mark.django_db
class TestTopicMoveForm(object):
    @pytest.fixture(autouse=True)
    def setup(self):
        # Create a basic user
        self.user = UserFactory.create()

        # Permission handler
        self.perm_handler = PermissionHandler()

        # Set up a top-level forum
        self.cat = create_category_forum()
        self.top_level_forum = create_forum()
        self.other_forum = create_forum()
        self.link = create_link_forum()

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

    def test_cannot_validate_if_the_user_cannot_move_forums(self):
        # Setup
        form = TopicMoveForm(
            data={
                'forum': self.cat.id,
            },
            topic=self.topic,
            user=self.user,
        )
        # Run
        is_valid = form.is_valid()
        # Check
        assert not is_valid

    def test_cannot_validate_if_the_forum_is_a_category(self):
        # Setup
        assign_perm('can_move_topics', self.user, self.cat)
        form = TopicMoveForm(
            data={
                'forum': self.cat.id,
            },
            topic=self.topic,
            user=self.user,
        )
        # Run
        is_valid = form.is_valid()
        # Check
        assert not is_valid

    def test_cannot_validate_if_the_forum_is_a_link(self):
        # Setup
        assign_perm('can_move_topics', self.user, self.link)
        form = TopicMoveForm(
            data={
                'forum': self.cat.id,
            },
            topic=self.topic,
            user=self.user,
        )
        # Run
        is_valid = form.is_valid()
        # Check
        assert not is_valid

    def test_cannot_validate_if_the_forum_is_the_topic_forum(self):
        # Setup
        assign_perm('can_move_topics', self.user, self.top_level_forum)
        form = TopicMoveForm(
            data={
                'forum': self.top_level_forum.id,
            },
            topic=self.topic,
            user=self.user,
        )
        # Run
        is_valid = form.is_valid()
        # Check
        assert not is_valid

    def test_validates_if_the_user_has_the_required_permission(self):
        # Setup
        assign_perm('can_move_topics', self.user, self.top_level_forum)
        assign_perm('can_move_topics', self.user, self.other_forum)
        form = TopicMoveForm(
            data={
                'forum': self.other_forum.id,
            },
            topic=self.topic,
            user=self.user,
        )
        # Run
        is_valid = form.is_valid()
        # Check
        assert is_valid

    def test_locks_the_topic_if_it_was_already_locked(self):
        # Setup
        assign_perm('can_move_topics', self.user, self.top_level_forum)
        assign_perm('can_move_topics', self.user, self.other_forum)
        self.topic.status = Topic.TOPIC_LOCKED
        self.topic.save()
        form = TopicMoveForm(
            data={
                'forum': self.other_forum.id,
            },
            topic=self.topic,
            user=self.user,
        )
        # Run & check
        assert form.fields['lock_topic'].initial
