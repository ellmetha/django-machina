# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.contrib.auth.models import User
from django.db.models import get_model
from django.template import Context
from django.template.base import Template
from django.test import TestCase
from guardian.shortcuts import assign_perm

# Local application / specific library imports
from machina.apps.conversation.abstract_models import TOPIC_STATUSES
from machina.apps.conversation.abstract_models import TOPIC_TYPES
from machina.apps.forum.abstract_models import FORUM_TYPES
from machina.core.loading import get_class
Forum = get_model('forum', 'Forum')
Post = get_model('conversation', 'Post')
Topic = get_model('conversation', 'Topic')

PermissionHandler = get_class('permission.handler', 'PermissionHandler')


class TestForumLastPostTag(TestCase):
    def setUp(self):
        self.loadstatement = '{% load forum_tags %}'
        self.user = User.objects.create(username='testuser')

        # Permission handler
        self.perm_handler = PermissionHandler()

        # Set up a top-level category
        top_level_cat = Forum.objects.create(name='top_level_cat', type=FORUM_TYPES.forum_cat)
        self.top_level_cat = top_level_cat

        # Set up some forums
        self.forum_1 = Forum.objects.create(parent=top_level_cat, name='forum_1', type=FORUM_TYPES.forum_post)
        self.forum_2 = Forum.objects.create(parent=top_level_cat, name='forum_2', type=FORUM_TYPES.forum_post)

        # Set up some topics and posts
        self.forum_1_topic = Topic.objects.create(subject='Test topic 1', forum=self.forum_1, poster=self.user,
                                                  type=TOPIC_TYPES.topic_post, status=TOPIC_STATUSES.topic_unlocked)
        self.post_1 = Post.objects.create(topic=self.forum_1_topic, poster=self.user, content='hello 1')

        # Assign some permissions
        assign_perm('can_see_forum', self.user, self.top_level_cat)
        assign_perm('can_see_forum', self.user, self.forum_1)

    def test_can_provide_the_last_post_of_a_forum(self):
        # Setup
        t = Template(self.loadstatement + '{% get_forum_last_post forum user as var %}')
        c = Context({'forum': self.forum_1, 'user': self.user})
        # Run
        rendered = t.render(c)
        # Check
        self.assertEqual(rendered, '')
        self.assertEqual(c['var'], self.post_1)
