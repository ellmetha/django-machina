# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.contrib.auth.models import User
from django.db.models import get_model
from guardian.shortcuts import assign_perm

# Local application / specific library imports
from machina.apps.forum.abstract_models import FORUM_TYPES
from machina.core.loading import get_class
from machina.test.testcases import BaseUnitTestCase
Forum = get_model('forum', 'Forum')
Post = get_model('conversation', 'Post')
Topic = get_model('conversation', 'Topic')

PermissionHandler = get_class('permission.handler', 'PermissionHandler')


class TestPermissionHandler(BaseUnitTestCase):
    def setUp(self):
        self.u1 = User.objects.create(username='user1')

        # Permission handler
        self.perm_handler = PermissionHandler()

        # Set up a top-level category
        top_level_cat = Forum.objects.create(name='top_level_cat', type=FORUM_TYPES.forum_cat)
        self.top_level_cat = top_level_cat

        # Set up some forums
        self.forum_1 = Forum.objects.create(parent=top_level_cat, name='forum_1', type=FORUM_TYPES.forum_post)
        self.forum_2 = Forum.objects.create(parent=top_level_cat, name='forum_2', type=FORUM_TYPES.forum_post)
        self.forum_3 = Forum.objects.create(parent=top_level_cat, name='forum_3', type=FORUM_TYPES.forum_link)

        # Set up a top-level forum link
        top_level_link = Forum.objects.create(name='top_level_link', type=FORUM_TYPES.forum_link)
        self.top_level_link = top_level_link

        # Assign some permissions
        assign_perm('can_see_forum', self.u1, self.forum_1)
        assign_perm('can_read_forum', self.u1, self.forum_3)

    def test_can_filter_a_list_of_forum_against_a_user(self):
        # Setup
        forums = Forum.objects.filter(parent=self.top_level_cat)
        # Run
        filtered_forums = self.perm_handler.forum_list_filter(forums, self.u1)
        # Check
        self.assertQuerysetEqual(filtered_forums, [self.forum_1, self.forum_3])
