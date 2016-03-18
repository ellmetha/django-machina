# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import pytest

from machina.core.db.models import get_model
from machina.test.factories import create_category_forum
from machina.test.factories import create_forum
from machina.test.factories import create_link_forum
from machina.test.factories import create_topic
from machina.test.factories import PostFactory
from machina.test.factories import UserFactory

Post = get_model('forum_conversation', 'Post')
Topic = get_model('forum_conversation', 'Topic')


@pytest.mark.django_db
class TestApprovedManager(object):
    @pytest.fixture(autouse=True)
    def setup(self):
        self.u1 = UserFactory.create()

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
        self.forum_3_topic_2 = create_topic(forum=self.forum_3, poster=self.u1, approved=False)

        # Set up some posts
        self.post_1 = PostFactory.create(topic=self.forum_1_topic, poster=self.u1)
        self.post_2 = PostFactory.create(topic=self.forum_3_topic, poster=self.u1)
        self.post_3 = PostFactory.create(topic=self.forum_3_topic, poster=self.u1, approved=False)

    def test_can_help_return_approved_topics(self):
        # Run
        topics = Topic.approved_objects.all()
        # Check
        assert set(topics) == set([self.forum_3_topic, self.forum_1_topic, ])

    def test_can_help_return_approved_posts(self):
        # Run
        posts = Post.approved_objects.all()
        # Check
        assert set(posts) == set([self.post_1, self.post_2, ])
