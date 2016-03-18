# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.sessions.middleware import SessionMiddleware
from django.template import Context
from django.template.base import Template
from django.template.loader import render_to_string
from django.test.client import RequestFactory
import pytest

from machina.apps.forum_permission.middleware import ForumPermissionMiddleware
from machina.core.db.models import get_model
from machina.core.loading import get_class
from machina.test.factories import create_category_forum
from machina.test.factories import create_forum
from machina.test.factories import create_topic
from machina.test.factories import PostFactory
from machina.test.factories import UserFactory

Forum = get_model('forum', 'Forum')
Post = get_model('forum_conversation', 'Post')
Topic = get_model('forum_conversation', 'Topic')

PermissionHandler = get_class('forum_permission.handler', 'PermissionHandler')
assign_perm = get_class('forum_permission.shortcuts', 'assign_perm')


@pytest.mark.django_db
class TestForumLastPostTag(object):
    @pytest.fixture(autouse=True)
    def setup(self):
        self.loadstatement = '{% load forum_tags %}'
        self.user = UserFactory.create()

        # Permission handler
        self.perm_handler = PermissionHandler()

        # Set up a top-level category
        self.top_level_cat = create_category_forum()

        # Set up some forums
        self.forum_1 = create_forum(parent=self.top_level_cat)
        self.forum_2 = create_forum(parent=self.top_level_cat)

        # Set up some topics and posts
        self.forum_1_topic = create_topic(forum=self.forum_1, poster=self.user)
        self.forum_2_topic = create_topic(forum=self.forum_2, poster=self.user)
        self.post_1 = PostFactory.create(topic=self.forum_1_topic, poster=self.user)
        self.post_2 = PostFactory.create(topic=self.forum_2_topic, poster=self.user)

        # Assign some permissions
        assign_perm('can_see_forum', self.user, self.top_level_cat)
        assign_perm('can_see_forum', self.user, self.forum_1)

    def test_can_provide_the_last_post_of_a_forum(self):
        # Setup
        t = Template(self.loadstatement + '{% get_forum_last_post forum user as var %}')
        c = Context({'forum': self.forum_1, 'user': self.user})
        # Run
        rendered = t.render(c)
        # Check
        assert rendered == ''
        assert c['var'] == self.post_1


@pytest.mark.django_db
class TestForumListTag(object):
    @pytest.fixture(autouse=True)
    def setup(self):
        self.loadstatement = '{% load forum_tags %}'
        self.request_factory = RequestFactory()
        self.user = UserFactory.create()

        # Set up a top-level category
        self.top_level_cat = create_category_forum()

        # Set up some forums
        self.forum_1 = create_forum(parent=self.top_level_cat)
        self.forum_2 = create_forum(parent=self.top_level_cat)

    def test_can_render_a_list_of_forums_according_to_their_minimum_tree_level(self):
        # Setup
        forums = Forum.objects.all()

        request = self.request_factory.get('/')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()

        request.user = self.user
        ForumPermissionMiddleware().process_request(request)
        t = Template(self.loadstatement + '{% forum_list forums %}')
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
        assert rendered != ''
        assert rendered == expected_out
