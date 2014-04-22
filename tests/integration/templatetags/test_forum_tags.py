# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.db.models import get_model
from django.template import Context
from django.template.base import Template
from django.template.loader import render_to_string
from django.test import TestCase
from django.test.client import RequestFactory
from guardian.shortcuts import assign_perm

# Local application / specific library imports
from machina.core.loading import get_class
from machina.test.factories import create_category_forum
from machina.test.factories import create_forum
from machina.test.factories import create_topic
from machina.test.factories import PostFactory
from machina.test.factories import UserFactory

Forum = get_model('forum', 'Forum')
Post = get_model('conversation', 'Post')
Topic = get_model('conversation', 'Topic')

PermissionHandler = get_class('permission.handler', 'PermissionHandler')


class TestForumLastPostTag(TestCase):
    def setUp(self):
        self.loadstatement = '{% load url from future %}{% load forum_tags %}'
        self.user = UserFactory.create()

        # Permission handler
        self.perm_handler = PermissionHandler()

        # Set up a top-level category
        self.top_level_cat = create_category_forum()

        # Set up some forums
        self.forum_1 = create_forum(parent=self.top_level_cat)
        self.forum_2 = create_forum(parent=self.top_level_cat)

        # Set up some topics and posts
        self.forum_1_topic = create_topic(forum=self.forum_1, poster=self.user)
        self.forum_2_topic = create_topic(forum=self.forum_2, poster=self.user)
        self.post_1 = PostFactory.create(topic=self.forum_1_topic, poster=self.user)
        self.post_2 = PostFactory.create(topic=self.forum_2_topic, poster=self.user)

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


class TestForumListTag(TestCase):
    def setUp(self):
        self.loadstatement = '{% load forum_tags %}'
        self.request_factory = RequestFactory()
        self.user = UserFactory.create()

        # Set up a top-level category
        self.top_level_cat = create_category_forum()

        # Set up some forums
        self.forum_1 = create_forum(parent=self.top_level_cat)
        self.forum_2 = create_forum(parent=self.top_level_cat)

    def test_can_render_a_list_of_forums_according_to_their_minimum_tree_level(self):
        # Setup
        forums = Forum.objects.all()
        request = self.request_factory.get('/')
        request.user = self.user
        t = Template(self.loadstatement + '{% forum_list forums request %}')
        c = Context({'forums': forums, 'request': request})
        expected_out = render_to_string(
            'machina/forum/forum_list.html',
            {
                'forums': forums,
                'user': self.user,
                'root_level': 0,
                'root_level_middle': 1,
                'root_level_sub': 2,
            }
        )
        # Run
        rendered = t.render(c)
        # Check
        self.assertNotEqual(rendered, '')
        self.assertEqual(rendered, expected_out)


class TestCanBeFilledByTag(TestCase):
    def setUp(self):
        self.loadstatement = '{% load forum_tags %}'
        self.request_factory = RequestFactory()
        self.user = UserFactory.create()

        # Set up a top-level category
        self.top_level_cat = create_category_forum()

        # Set up some forums
        self.forum_1 = create_forum(parent=self.top_level_cat)
        self.forum_2 = create_forum(parent=self.top_level_cat)

        # Assign some permissions
        assign_perm('can_start_new_topics', self.user, self.forum_1)

    def test_can_tell_if_a_user_can_create_topics(self):
        # Setup
        def get_rendered(forum, user):
            request = self.request_factory.get('/')
            request.user = user
            t = Template(self.loadstatement + '{% if forum|can_be_filled_by:request.user %}CAN_START_TOPICS{% else %}CANNOT_START_TOPICS{% endif %}')
            c = Context({'forum': forum, 'request': request})
            rendered = t.render(c)

            return rendered

        # Run & check
        self.assertEqual(get_rendered(self.forum_1, self.user), 'CAN_START_TOPICS')
        self.assertEqual(get_rendered(self.forum_2, self.user), 'CANNOT_START_TOPICS')
