# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.db.models import get_model

# Local application / specific library imports
from machina.test.factories import create_category_forum
from machina.test.factories import create_forum
from machina.test.factories import create_link_forum
from machina.test.factories import create_topic
from machina.test.factories import ForumReadTrackFactory
from machina.test.factories import PostFactory
from machina.test.factories import UserFactory
from machina.test.testcases import BaseUnitTestCase

ForumReadTrack = get_model('forum_tracking', 'ForumReadTrack')


class TestForumReadTrackManager(BaseUnitTestCase):
    def setUp(self):
        self.u1 = UserFactory.create()
        self.u2 = UserFactory.create()

        self.top_level_cat_1 = create_category_forum()
        self.top_level_cat_2 = create_category_forum()

        self.forum_1 = create_forum(parent=self.top_level_cat_1)
        self.forum_2 = create_forum(parent=self.top_level_cat_1)
        self.forum_2_child_1 = create_link_forum(parent=self.forum_2)
        self.forum_2_child_2 = create_forum(parent=self.forum_2)
        self.forum_3 = create_forum(parent=self.top_level_cat_1)

        self.forum_4 = create_forum(parent=self.top_level_cat_2)

        self.topic = create_topic(forum=self.forum_2, poster=self.u1)
        PostFactory.create(topic=self.topic, poster=self.u1)

        # Initially u2 read the previously created topic
        ForumReadTrackFactory.create(forum=self.forum_2, user=self.u2)

    def test_can_tell_if_a_forum_is_unread(self):
        # Setup
        PostFactory.create(topic=self.topic, poster=self.u1)
        # Run
        unread_forums = ForumReadTrack.objects.get_unread_forums_from_list(
            self.top_level_cat_1.get_descendants(include_self=True),
            self.u2)
        # Check
        self.assertIn(self.forum_2, unread_forums)

    def test_tells_that_the_ancestors_of_an_unread_forum_are_also_unread(self):
        # Setup
        PostFactory.create(topic=self.topic, poster=self.u1)
        # Run
        unread_forums = ForumReadTrack.objects.get_unread_forums_from_list(
            self.top_level_cat_1.get_descendants(include_self=True),
            self.u2)
        # Check
        self.assertQuerysetEqual(unread_forums, [
            self.top_level_cat_1,
            self.forum_2])

    def test_cannot_tell_that_the_descendant_of_an_unread_forum_are_also_unread(self):
        # Setup
        PostFactory.create(topic=self.topic, poster=self.u1)
        # Run
        unread_forums = ForumReadTrack.objects.get_unread_forums_from_list(
            self.top_level_cat_1.get_descendants(include_self=True),
            self.u2)
        # Check
        self.assertNotIn(self.forum_2_child_2, unread_forums)

    def test_considers_a_forum_as_unread_without_tracks_if_it_has_topics(self):
        # Setup
        new_topic = create_topic(forum=self.forum_2_child_2, poster=self.u2)
        PostFactory.create(topic=new_topic, poster=self.u2)
        # Run
        unread_forums = ForumReadTrack.objects.get_unread_forums_from_list(
            self.top_level_cat_1.get_descendants(include_self=True),
            self.u1)
        # Check
        self.assertIn(self.forum_2_child_2, unread_forums)
