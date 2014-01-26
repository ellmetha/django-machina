# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.db.models import get_model
from guardian.shortcuts import assign_perm
from guardian.shortcuts import remove_perm

# Local application / specific library imports
from machina.apps.conversation.abstract_models import TOPIC_STATUSES
from machina.apps.conversation.abstract_models import TOPIC_TYPES
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
        self.g1 = Group.objects.create(name='group1')
        self.u1.groups.add(self.g1)

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

        # Set up some topics
        self.forum_1_topic = Topic.objects.create(subject='Test topic 1', forum=self.forum_1, poster=self.u1,
                                                  type=TOPIC_TYPES.topic_post, status=TOPIC_STATUSES.topic_unlocked)
        self.forum_3_topic = Topic.objects.create(subject='Test topic 2', forum=self.forum_3, poster=self.u1,
                                                  type=TOPIC_TYPES.topic_post, status=TOPIC_STATUSES.topic_unlocked)

        # Set up some posts
        self.post_1 = Post.objects.create(topic=self.forum_1_topic, poster=self.u1, content='hello 1')
        self.post_2 = Post.objects.create(topic=self.forum_3_topic, poster=self.u1, content='hello 2')

        # Assign some permissions
        assign_perm('can_see_forum', self.u1, self.top_level_cat)
        assign_perm('can_see_forum', self.u1, self.forum_1)
        assign_perm('can_read_forum', self.g1, self.forum_3)

    def test_show_a_forum_if_it_is_visible(self):
        # Setup
        forums = Forum.objects.filter(pk=self.top_level_cat.pk)
        # Run
        filtered_forums = self.perm_handler.forum_list_filter(forums, self.u1)
        # Check
        self.assertQuerysetEqual(filtered_forums, [self.top_level_cat, ])

    def test_hide_a_forum_if_it_is_not_visible(self):
        # Setup
        forums = Forum.objects.filter(pk=self.top_level_cat.pk)
        # Run
        filtered_forums = self.perm_handler.forum_list_filter(forums, self.u1)
        # Check
        self.assertQuerysetEqual(filtered_forums, [self.top_level_cat, ])

    def test_show_a_forum_if_all_of_its_ancestors_are_visible(self):
        # Setup
        forums = Forum.objects.filter(parent=self.top_level_cat)
        # Run
        filtered_forums = self.perm_handler.forum_list_filter(forums, self.u1)
        # Check
        self.assertQuerysetEqual(filtered_forums, [self.forum_1, self.forum_3])

    def test_hide_a_forum_if_one_of_its_ancestors_is_not_visible(self):
        # Setup
        remove_perm('can_see_forum', self.u1, self.top_level_cat)
        forums = Forum.objects.filter(parent=self.top_level_cat)
        # Run
        filtered_forums = self.perm_handler.forum_list_filter(forums, self.u1)
        # Check
        self.assertQuerysetEqual(filtered_forums, [])

    def test_knows_the_last_topic_visible_inside_a_forum(self):
        # Run & check : no forum hidden
        last_post = self.perm_handler.get_forum_last_post(self.top_level_cat, self.u1)
        self.assertEqual(last_post, self.post_2)

        # Run & check : one forum hidden
        remove_perm('can_read_forum', self.g1, self.forum_3)
        last_post = self.perm_handler.get_forum_last_post(self.top_level_cat, self.u1)
        self.assertEqual(last_post, self.post_1)

        # Run & check : all forums hidden
        remove_perm('can_see_forum', self.u1, self.forum_1)
        last_post = self.perm_handler.get_forum_last_post(self.top_level_cat, self.u1)
        self.assertIsNone(last_post)
