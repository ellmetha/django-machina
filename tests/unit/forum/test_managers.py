# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import pytest

from machina.core.db.models import get_model
from machina.test.factories import create_category_forum
from machina.test.factories import create_forum
from machina.test.factories import create_link_forum

Forum = get_model('forum', 'Forum')


@pytest.mark.django_db
class TestForumManager(object):
    @pytest.fixture(autouse=True)
    def setup(self):
        # Set up the following forum tree:
        #
        #     top_level_cat
        #         forum_1
        #         forum_2
        #             forum_2_child_1
        #             forum_2_child_2
        #                 forum_2_child_2_1
        #                 forum_2_child_2_2
        #     top_level_forum_1
        #     top_level_forum_2
        #         sub_cat
        #             sub_sub_forum
        #     top_level_forum_3
        #         forum_3
        #             forum_3_child_1
        #                 forum_3_child_1_1
        #                     deep_forum
        #     last_forum
        #
        self.top_level_cat = create_category_forum()

        self.forum_1 = create_forum(parent=self.top_level_cat)
        self.forum_2 = create_forum(parent=self.top_level_cat)
        self.forum_2_child_1 = create_link_forum(parent=self.forum_2)
        self.forum_2_child_2 = create_forum(parent=self.forum_2)
        self.forum_2_child_2_1 = create_forum(parent=self.forum_2_child_2)
        self.forum_2_child_2_2 = create_forum(parent=self.forum_2_child_2)

        self.top_level_forum_1 = create_forum()

        self.top_level_forum_2 = create_forum()
        self.sub_cat = create_category_forum(parent=self.top_level_forum_2)
        self.sub_sub_forum = create_forum(parent=self.sub_cat)

        self.top_level_forum_3 = create_forum()
        self.forum_3 = create_forum(parent=self.top_level_forum_3)
        self.forum_3_child_1 = create_forum(parent=self.forum_3)
        self.forum_3_child_1_1 = create_forum(parent=self.forum_3_child_1)
        self.deep_forum = create_forum(parent=self.forum_3_child_1_1)

        self.last_forum = create_forum()

    def test_can_return_a_list_of_displayable_forums_from_the_root(self):
        # Run & check
        displayable_forums = Forum.objects.displayable_subforums()
        assert set(displayable_forums) == set([
            self.top_level_cat,
            self.forum_1,
            self.forum_2,
            self.forum_2_child_1,
            self.forum_2_child_2,
            self.top_level_forum_1,
            self.top_level_forum_2,
            self.sub_cat,
            self.top_level_forum_3,
            self.forum_3,
            self.last_forum])

    def test_can_return_a_list_of_displayable_forums_from_a_given_forum(self):
        # Run & check
        displayable_forums = Forum.objects.displayable_subforums(start_from=self.top_level_cat)
        assert set(displayable_forums) == set([
            self.forum_1,
            self.forum_2,
            self.forum_2_child_1,
            self.forum_2_child_2])
        displayable_forums = Forum.objects.displayable_subforums(start_from=self.top_level_forum_3)
        assert set(displayable_forums) == set([
            self.forum_3,
            self.forum_3_child_1])
        displayable_forums = Forum.objects.displayable_subforums(start_from=self.last_forum)
        assert list(displayable_forums) == []
