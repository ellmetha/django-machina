# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import unicode_literals

# Third party imports
import pytest

# Local application / specific library imports
from machina.core.db.models import get_model
from machina.core.utils import refresh
from machina.test.factories import create_forum
from machina.test.factories import create_topic
from machina.test.factories import PostFactory
from machina.test.factories import UserFactory

ForumProfile = get_model('forum_member', 'ForumProfile')


@pytest.mark.django_db
class TestDecreasePostsCountReceiver(object):
    def test_can_decrease_the_posts_count_of_the_post_being_deleted(self):
        # Setup
        u1 = UserFactory.create()
        top_level_forum = create_forum()
        topic = create_topic(forum=top_level_forum, poster=u1)
        PostFactory.create(topic=topic, poster=u1)
        post = PostFactory.create(topic=topic, poster=u1)
        profile = ForumProfile.objects.get(user=u1)
        initial_posts_count = profile.posts_count
        # Run
        post.delete()
        # Check
        profile = refresh(profile)
        assert profile.posts_count == initial_posts_count - 1

    def test_do_nothing_if_the_poster_is_anonymous(self):
        # Setup
        top_level_forum = create_forum()
        topic = create_topic(forum=top_level_forum, poster=None)
        post = PostFactory.create(topic=topic, poster=None, username='test')
        # Run
        post.delete()
        # Check
        assert ForumProfile.objects.exists() is False
