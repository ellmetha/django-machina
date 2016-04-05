# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.sessions.middleware import SessionMiddleware
from django.template import Context
from django.template.base import Template
from django.template.loader import render_to_string
from django.test.client import RequestFactory
import pytest

from machina.core.db.models import get_model
from machina.core.loading import get_class
from machina.test.factories import create_category_forum
from machina.test.factories import create_forum
from machina.test.factories import create_topic
from machina.test.factories import GroupFactory
from machina.test.factories import PostFactory
from machina.test.factories import UserFactory

Forum = get_model('forum', 'Forum')
Post = get_model('forum_conversation', 'Post')
Topic = get_model('forum_conversation', 'Topic')

PermissionHandler = get_class('forum_permission.handler', 'PermissionHandler')
assign_perm = get_class('forum_permission.shortcuts', 'assign_perm')


@pytest.mark.django_db
class BaseConversationTagsTestCase(object):
    @pytest.fixture(autouse=True)
    def setup(self):
        self.loadstatement = '{% load forum_conversation_tags %}'
        self.request_factory = RequestFactory()

        self.g1 = GroupFactory.create()
        self.u1 = UserFactory.create()
        self.u2 = UserFactory.create()
        self.u1.groups.add(self.g1)
        self.u2.groups.add(self.g1)
        self.moderators = GroupFactory.create()
        self.moderator = UserFactory.create()
        self.moderator.groups.add(self.moderators)
        self.superuser = UserFactory.create(is_superuser=True)

        # Permission handler
        self.perm_handler = PermissionHandler()

        # Set up a top-level category
        self.top_level_cat = create_category_forum()

        # Set up some forums
        self.forum_1 = create_forum(parent=self.top_level_cat)
        self.forum_2 = create_forum(parent=self.top_level_cat)

        # Set up some topics and posts
        self.forum_1_topic = create_topic(forum=self.forum_1, poster=self.u1)
        self.forum_2_topic = create_topic(forum=self.forum_2, poster=self.u2)
        self.post_1 = PostFactory.create(topic=self.forum_1_topic, poster=self.u1)
        self.post_2 = PostFactory.create(topic=self.forum_2_topic, poster=self.u2)

        # Assign some permissions
        assign_perm('can_see_forum', self.g1, self.forum_1)
        assign_perm('can_read_forum', self.g1, self.forum_1)
        assign_perm('can_edit_own_posts', self.g1, self.forum_1)
        assign_perm('can_delete_own_posts', self.g1, self.forum_1)
        assign_perm('can_reply_to_topics', self.g1, self.forum_1)
        assign_perm('can_see_forum', self.moderators, self.forum_1)
        assign_perm('can_read_forum', self.moderators, self.forum_1)
        assign_perm('can_edit_own_posts', self.moderators, self.forum_1)
        assign_perm('can_delete_own_posts', self.moderators, self.forum_1)
        assign_perm('can_edit_posts', self.moderators, self.forum_1)
        assign_perm('can_delete_posts', self.moderators, self.forum_1)

    def get_request(self, url='/'):
        request = self.request_factory.get('/')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        return request


class TestPostedByTag(BaseConversationTagsTestCase):
    def test_can_tell_if_the_user_is_the_owner_of_a_post(self):
        # Setup
        def get_rendered(post, user):
            request = self.get_request()
            request.user = user
            t = Template(
                self.loadstatement +
                '{% if post|posted_by:request.user %}OWNER{% else %}NO_OWNER{% endif %}')
            c = Context({'post': post, 'request': request})
            rendered = t.render(c)

            return rendered

        # Run & check
        assert get_rendered(self.post_1, self.u1) == 'OWNER'
        assert get_rendered(self.post_2, self.u1) == 'NO_OWNER'


class TestTopicPagesInlineListTag(BaseConversationTagsTestCase):
    def test_provides_the_number_of_pages_of_a_topic(self):
        # Setup
        def get_rendered(topic):
            t = Template(self.loadstatement + '{% topic_pages_inline_list topic %}')
            c = Context({'topic': topic})
            rendered = t.render(c)

            return rendered

        for i in range(0, 35):
            PostFactory.create(topic=self.forum_1_topic, poster=self.u1)
        expected_out_small = render_to_string(
            'machina/forum_conversation/topic_pages_inline_list.html',
            {
                'topic': self.forum_1_topic,
                'first_pages': [1, 2, 3, ],
            }
        )

        for i in range(0, 120):
            PostFactory.create(topic=self.forum_2_topic, poster=self.u1)
        expected_out_huge = render_to_string(
            'machina/forum_conversation/topic_pages_inline_list.html',
            {
                'topic': self.forum_2_topic,
                'first_pages': [1, 2, 3, 4, ],
                'last_page': 9,
            }
        )

        # Run
        rendered_small = get_rendered(self.forum_1_topic)
        rendered_huge = get_rendered(self.forum_2_topic)

        # Check
        assert rendered_small == expected_out_small
        assert rendered_huge == expected_out_huge
