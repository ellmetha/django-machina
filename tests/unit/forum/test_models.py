# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.exceptions import ValidationError
import pytest

from machina.core.db.models import get_model
from machina.test.factories import build_category_forum
from machina.test.factories import build_link_forum
from machina.test.factories import create_category_forum
from machina.test.factories import create_forum
from machina.test.factories import create_link_forum
from machina.test.factories import create_topic
from machina.test.factories import PostFactory
from machina.test.factories import UserFactory

Forum = get_model('forum', 'Forum')
Post = get_model('forum_conversation', 'Post')
Topic = get_model('forum_conversation', 'Topic')


@pytest.mark.django_db
class TestForum(object):
    @pytest.fixture(autouse=True)
    def setup(self):
        self.u1 = UserFactory.create()

        # Set up top-level forums: a category, a default forum and a link forum
        self.top_level_cat = create_category_forum()
        self.top_level_forum = create_forum()
        self.top_level_link = create_link_forum()

    def test_has_a_margin_level_two_times_greater_than_its_real_level(self):
        # Run
        sub_level_forum = create_forum(parent=self.top_level_forum)
        # Check
        assert self.top_level_forum.margin_level == 0
        assert sub_level_forum.margin_level == 2

    def test_category_cannot_be_the_child_of_another_category(self):
        # Run & check
        with pytest.raises(ValidationError):
            cat = build_category_forum(parent=self.top_level_cat)
            cat.full_clean()

    def test_can_not_be_the_child_of_a_forum_link(self):
        # Run & check
        for forum_type, _ in Forum.TYPE_CHOICES:
            with pytest.raises(ValidationError):
                forum = build_link_forum(parent=self.top_level_link)
                forum.full_clean()

    def test_must_have_a_link_in_case_of_a_link_forum(self):
        # Run & check
        with pytest.raises(ValidationError):
            forum = Forum(parent=self.top_level_forum, name='sub_link_forum', type=Forum.FORUM_LINK)
            forum.full_clean()

    def test_saves_its_numbers_of_posts_and_topics(self):
        # Run & check
        topic = create_topic(forum=self.top_level_forum, poster=self.u1)
        PostFactory.create(topic=topic, poster=self.u1)
        PostFactory.create(topic=topic, poster=self.u1)
        assert self.top_level_forum.posts_count == topic.posts.filter(approved=True).count()
        assert self.top_level_forum.topics_count == self.top_level_forum.topics.count()

        topic2 = create_topic(forum=self.top_level_forum, poster=self.u1, approved=False)
        PostFactory.create(topic=topic2, poster=self.u1, approved=False)
        assert self.top_level_forum.posts_count == \
            topic.posts.filter(approved=True).count() + topic2.posts.filter(approved=True).count()
        assert self.top_level_forum.topics_count == \
            self.top_level_forum.topics.filter(approved=True).count()

    def test_can_indicate_its_appartenance_to_a_forum_type(self):
        # Run & check
        assert self.top_level_cat.is_category
        assert self.top_level_forum.is_forum
        assert self.top_level_link.is_link

    def test_can_trigger_the_update_of_the_counters_of_a_new_parent(self):
        # Setup
        topic = create_topic(forum=self.top_level_forum, poster=self.u1)
        PostFactory.create(topic=topic, poster=self.u1)
        PostFactory.create(topic=topic, poster=self.u1)
        # Run
        self.top_level_forum.parent = self.top_level_cat
        self.top_level_forum.save()
        # Check
        assert self.top_level_cat.posts_count == self.top_level_forum.posts_count
        assert self.top_level_cat.topics_count == self.top_level_forum.topics_count

    def test_can_trigger_the_update_of_the_counters_of_a_previous_parent(self):
        # Setup
        sub_level_forum = create_forum(parent=self.top_level_forum)
        topic = create_topic(forum=sub_level_forum, poster=self.u1)
        PostFactory.create(topic=topic, poster=self.u1)
        PostFactory.create(topic=topic, poster=self.u1)
        # Run
        sub_level_forum.parent = self.top_level_cat
        sub_level_forum.save()
        # Check
        self.top_level_forum = Forum.objects.get(pk=self.top_level_forum.pk)
        assert self.top_level_forum.posts_count == 0
        assert self.top_level_forum.topics_count == 0

    def test_stores_its_last_post_datetime(self):
        # Setup
        sub_level_forum = create_forum(parent=self.top_level_forum)
        topic = create_topic(forum=sub_level_forum, poster=self.u1)
        PostFactory.create(topic=topic, poster=self.u1)
        # Run
        p2 = PostFactory.create(topic=topic, poster=self.u1)
        # Check
        sub_level_forum.refresh_from_db()
        assert sub_level_forum.last_post_on == p2.created

    def test_can_reset_last_post_datetime_if_all_topics_have_been_deleted(self):
        # Setup
        sub_level_forum = create_forum(parent=self.top_level_forum)
        topic = create_topic(forum=sub_level_forum, poster=self.u1)
        PostFactory.create(topic=topic, poster=self.u1)
        # Run
        topic.delete()
        # Check
        sub_level_forum.refresh_from_db()
        assert sub_level_forum.last_post_on is None
