# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.exceptions import ValidationError
from faker import Factory as FakerFactory
import pytest

from machina.core.db.models import get_model
from machina.test.factories import build_topic
from machina.test.factories import create_category_forum
from machina.test.factories import create_forum
from machina.test.factories import create_link_forum
from machina.test.factories import create_topic
from machina.test.factories import PostFactory
from machina.test.factories import UserFactory

faker = FakerFactory.create()

Forum = get_model('forum', 'Forum')
ForumProfile = get_model('forum_member', 'ForumProfile')
Post = get_model('forum_conversation', 'Post')
Topic = get_model('forum_conversation', 'Topic')


@pytest.mark.django_db
class TestTopic(object):
    @pytest.fixture(autouse=True)
    def setup(self):
        self.u1 = UserFactory.create()

        # Set up a top-level forum, an associated topic and a post
        self.top_level_forum = create_forum()
        self.topic = create_topic(forum=self.top_level_forum, poster=self.u1)
        self.post = PostFactory.create(topic=self.topic, poster=self.u1)

    def test_knows_if_it_is_a_default_topic(self):
        # Run & check
        assert self.topic.is_topic

    def test_knows_if_it_is_sticky(self):
        # Setup
        sticky_topic = create_topic(
            forum=self.top_level_forum, poster=self.u1,
            type=Topic.TOPIC_STICKY)
        # Run & check
        assert sticky_topic.is_sticky

    def test_knows_if_it_is_an_announce(self):
        # Setup
        announce = create_topic(
            forum=self.top_level_forum, poster=self.u1,
            type=Topic.TOPIC_ANNOUNCE)
        # Run & check
        assert announce.is_announce

    def test_knows_if_it_is_locked(self):
        # Run & check
        assert not self.topic.is_locked
        self.topic.status = self.topic.TOPIC_LOCKED
        self.topic.save()
        assert self.topic.is_locked

    def test_has_a_first_post(self):
        # Run & check
        assert self.topic.first_post == self.post
        PostFactory.create(topic=self.topic, poster=self.u1)
        assert self.topic.first_post == self.post

    def test_has_a_last_post(self):
        # Setup
        new_topic = create_topic(forum=self.top_level_forum, poster=self.u1)
        # Run & check
        middle_post = PostFactory.create(topic=self.topic, poster=self.u1)
        assert self.topic.last_post == middle_post
        new_last_post = Post.objects.create(topic=self.topic, poster=self.u1, content='last')
        assert self.topic.last_post == new_last_post
        assert new_topic.last_post is None

    def test_cannot_tell_that_a_non_approved_post_is_the_last_post(self):
        # Setup
        create_topic(forum=self.top_level_forum, poster=self.u1)
        # Run & check
        middle_post = PostFactory.create(topic=self.topic, poster=self.u1)
        PostFactory.create(topic=self.topic, poster=self.u1, approved=False)
        self.topic.refresh_from_db()
        assert self.topic.last_post == middle_post

    def test_cannot_update_its_last_post_date_with_the_creation_date_of_a_non_approved_post(self):
        # Setup
        create_topic(forum=self.top_level_forum, poster=self.u1)
        # Run & check
        middle_post = PostFactory.create(topic=self.topic, poster=self.u1)
        PostFactory.create(topic=self.topic, poster=self.u1, approved=False)
        self.topic.refresh_from_db()
        assert self.topic.last_post_on == middle_post.created

    def test_has_the_first_post_name_as_subject(self):
        # Run & check
        assert self.topic.subject == self.post.subject

    def test_has_the_same_approved_status_as_its_first_post(self):
        # Run & check
        assert self.topic.approved == self.post.approved
        self.post.approved = False
        self.post.save()
        assert self.topic.approved == self.post.approved

    def test_saves_its_number_of_posts(self):
        # Run & check
        post = PostFactory.create(topic=self.topic, poster=self.u1)
        initial_count = self.topic.posts.count()
        assert initial_count == self.topic.posts_count
        post.delete()
        assert initial_count - 1 == self.topic.posts_count

    def test_saves_only_its_number_of_approved_posts(self):
        # Run & check
        post = PostFactory.create(topic=self.topic, poster=self.u1, approved=False)
        initial_count = self.topic.posts.filter(approved=True).count()
        assert initial_count == self.topic.posts_count
        post.delete()
        assert initial_count == self.topic.posts_count

    def test_can_not_be_associated_with_a_forum_link_or_a_forum_category(self):
        # Setup
        top_level_cat = create_category_forum()
        top_level_link = create_link_forum()
        # Run & check
        with pytest.raises(ValidationError):
            new_topic = build_topic(forum=top_level_cat, poster=self.u1)
            new_topic.full_clean()
        with pytest.raises(ValidationError):
            new_topic = build_topic(forum=top_level_link, poster=self.u1)
            new_topic.full_clean()

    def test_save_can_trigger_the_update_of_the_counters_of_a_new_forum(self):
        # Setup
        new_top_level_forum = create_forum()
        # Run
        self.topic.forum = new_top_level_forum
        self.topic.save()
        # Check
        assert self.topic.forum == new_top_level_forum
        assert new_top_level_forum.topics_count == 1
        assert new_top_level_forum.posts_count == self.topic.posts_count

    def test_can_trigger_the_update_of_the_counters_of_a_previous_forum(self):
        # Setup
        new_top_level_forum = create_forum()
        # Run
        self.topic.forum = new_top_level_forum
        self.topic.save()
        # Check
        self.top_level_forum = Forum.objects.get(pk=self.top_level_forum.pk)
        assert self.topic.forum == new_top_level_forum
        assert self.top_level_forum.topics_count == 0
        assert self.top_level_forum.posts_count == 0


@pytest.mark.django_db
class TestPost(object):
    @pytest.fixture(autouse=True)
    def setup(self):
        self.u1 = UserFactory.create()

        # Set up a top-level forum, an associated topic and a post
        self.top_level_forum = create_forum()
        self.topic = create_topic(forum=self.top_level_forum, poster=self.u1)
        self.post = PostFactory.create(topic=self.topic, poster=self.u1)

        self.topic_pk = self.topic.pk

    def test_knows_if_it_is_the_topic_head(self):
        # Check
        assert self.post.is_topic_head == (self.post.topic.posts.count() == 1)

    def test_knows_if_it_is_the_topic_tail(self):
        # Run & check
        post = PostFactory.create(topic=self.topic, poster=self.u1)
        assert post.is_topic_tail

    def test_knows_if_it_is_alone_in_the_topic(self):
        # Run & check
        assert self.post.is_alone

    def test_knows_its_position_inside_the_topic(self):
        # Setup
        post_2 = PostFactory.create(topic=self.topic, poster=self.u1)
        post_3 = PostFactory.create(topic=self.topic, poster=self.u1)
        # Run & check
        assert self.post.position == 1
        assert post_2.position == 2
        assert post_3.position == 3

    def test_is_both_topic_head_and_tail_if_it_is_alone_in_the_topic(self):
        # Check
        assert self.post.is_topic_head
        assert self.post.is_topic_tail

    def test_deletion_should_result_in_the_topic_deletion_if_it_is_alone_in_the_topic(self):
        # Run
        self.post.delete()
        # Check
        with pytest.raises(Topic.DoesNotExist):
            Topic.objects.get(pk=self.topic_pk)

    def test_deletion_should_result_in_the_topic_deletion_if_it_is_alone_in_the_topic_and_not_approved(self):  # noqa
        # Run
        self.post.approved = False
        self.post.save()
        self.post.delete()
        # Check
        with pytest.raises(Topic.DoesNotExist):
            Topic.objects.get(pk=self.topic_pk)

    def test_save_triggers_the_update_of_the_member_posts_count_if_the_related_post_is_approved(self):  # noqa
        # Setup
        post = PostFactory.build(topic=self.topic, poster=self.u1)
        profile = ForumProfile.objects.get(user=self.u1)
        initial_posts_count = profile.posts_count
        # Run
        post.save()
        # Check
        profile.refresh_from_db()
        assert profile.posts_count == initial_posts_count + 1

    def test_save_cannot_trigger_the_update_of_the_member_posts_count_if_the_related_post_is_not_approved(self):  # noqa
        # Setup
        post = PostFactory.build(topic=self.topic, poster=self.u1, approved=False)
        profile = ForumProfile.objects.get(user=self.u1)
        initial_posts_count = profile.posts_count
        # Run
        post.save()
        # Check
        profile.refresh_from_db()
        assert profile.posts_count == initial_posts_count

    def test_save_trigger_the_update_of_the_member_posts_count_if_the_related_post_switch_to_approved(self):  # noqa
        # Setup
        post = PostFactory.create(topic=self.topic, poster=self.u1, approved=False)
        profile = ForumProfile.objects.get(user=self.u1)
        initial_posts_count = profile.posts_count
        # Run
        post.approved = True
        post.save()
        # Check
        profile.refresh_from_db()
        assert profile.posts_count == initial_posts_count + 1

    def test_cannot_be_cleaned_if_it_is_not_associated_with_a_user_or_an_anonymous_user(self):
        # Run & check
        with pytest.raises(ValidationError):
            post = PostFactory.build(topic=self.topic, poster=None, anonymous_key=None)
            post.clean()

    def test_cannot_be_cleaned_if_it_is_not_associated_with_a_user_and_an_anonymous_user(self):
        # Run & check
        with pytest.raises(ValidationError):
            post = PostFactory.build(topic=self.topic, poster=self.u1, anonymous_key='1234')
            post.clean()

    def test_cannot_be_cleaned_if_the_anonymous_poster_username_is_not_specified(self):
        # Run & check
        with pytest.raises(ValidationError):
            post = PostFactory.build(topic=self.topic, poster=None, anonymous_key='1234')
            post.clean()
