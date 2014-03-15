# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.db.models import get_model
from django.template import Context
from django.template.base import Template
from django.test import TestCase
from django.test.client import RequestFactory
from guardian.shortcuts import assign_perm

# Local application / specific library imports
from machina.conf import settings
from machina.core.loading import get_class
from machina.test.factories import create_category_forum
from machina.test.factories import create_forum
from machina.test.factories import create_topic
from machina.test.factories import GroupFactory
from machina.test.factories import PostFactory
from machina.test.factories import UserFactory

Forum = get_model('forum', 'Forum')
Post = get_model('conversation', 'Post')
Topic = get_model('conversation', 'Topic')

PermissionHandler = get_class('permission.handler', 'PermissionHandler')


class BaseConversationTagsTestCase(TestCase):
    def setUp(self):
        self.loadstatement = '{% load url from future %}{% load conversation_tags %}'
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

        # Set up some topics and posts
        self.forum_1_topic = create_topic(forum=self.forum_1, poster=self.u1)
        self.forum_2_topic = create_topic(forum=self.forum_2, poster=self.u2)
        self.post_1 = PostFactory.create(topic=self.forum_1_topic, poster=self.u1)
        self.post_2 = PostFactory.create(topic=self.forum_2_topic, poster=self.u2)

        # Assign some permissions
        assign_perm('can_see_forum', self.g1, self.forum_1)
        assign_perm('can_read_forum', self.g1, self.forum_1)
        assign_perm('can_edit_own_posts', self.g1, self.forum_1)
        assign_perm('can_delete_own_posts', self.g1, self.forum_1)
        assign_perm('can_see_forum', self.moderators, self.forum_1)
        assign_perm('can_read_forum', self.moderators, self.forum_1)
        assign_perm('can_edit_own_posts', self.moderators, self.forum_1)
        assign_perm('can_delete_own_posts', self.moderators, self.forum_1)
        assign_perm('can_edit_posts', self.moderators, self.forum_1)
        assign_perm('can_delete_posts', self.moderators, self.forum_1)


class TestPageNumberTag(BaseConversationTagsTestCase):
    def test_knows_the_page_associated_with_a_topic_post(self):
        # Setup
        def get_rendered(post):
            request = self.request_factory.get('/')
            t = Template(self.loadstatement + '{{ post|page_number }}')
            c = Context({'post': post, 'request': request})
            rendered = t.render(c)

            return rendered

        settings.TOPIC_POSTS_NUMBER_PER_PAGE = 10
        for i in range(20):
            post = PostFactory.create(topic=self.forum_1_topic, poster=self.u1)
            setattr(self, 'new_post_' + str(i), post)

        # Run & check
        self.assertEqual(get_rendered(self.new_post_5), '1')
        self.assertEqual(get_rendered(self.new_post_12), '2')


class TestPostedByTag(BaseConversationTagsTestCase):
    def test_can_tell_if_the_logged_in_user_is_the_owner_of_a_post(self):
        # Setup
        def get_rendered(post, user):
            request = self.request_factory.get('/')
            request.user = user
            t = Template(self.loadstatement + '{% if post|posted_by:request.user %}OWNER{% else %}NO_OWNER{% endif %}')
            c = Context({'post': post, 'request': request})
            rendered = t.render(c)

            return rendered

        # Run & check
        self.assertEqual(get_rendered(self.post_1, self.u1), 'OWNER')
        self.assertEqual(get_rendered(self.post_2, self.u1), 'NO_OWNER')


class TestCanBeEditedByTag(BaseConversationTagsTestCase):
    def test_can_tell_if_the_logged_in_user_can_edit_a_post(self):
        # Setup
        def get_rendered(post, user):
            request = self.request_factory.get('/')
            request.user = user
            t = Template(self.loadstatement + '{% if post|can_be_edited_by:request.user %}CAN_EDIT{% else %}CANNOT_EDIT{% endif %}')
            c = Context({'post': post, 'request': request})
            rendered = t.render(c)

            return rendered

        # Run & check
        self.assertEqual(get_rendered(self.post_1, self.u1), 'CAN_EDIT')
        self.assertEqual(get_rendered(self.post_1, self.u2), 'CANNOT_EDIT')
        self.assertEqual(get_rendered(self.post_1, self.moderator), 'CAN_EDIT')
        self.assertEqual(get_rendered(self.post_1, self.superuser), 'CAN_EDIT')


class TestCanBeDeleteddByTag(BaseConversationTagsTestCase):
    def test_can_tell_if_the_logged_in_user_can_edit_a_post(self):
        # Setup
        def get_rendered(post, user):
            request = self.request_factory.get('/')
            request.user = user
            t = Template(self.loadstatement + '{% if post|can_be_deleted_by:request.user %}CAN_DELETE{% else %}CANNOT_DELETE{% endif %}')
            c = Context({'post': post, 'request': request})
            rendered = t.render(c)

            return rendered

        # Run & check
        self.assertEqual(get_rendered(self.post_1, self.u1), 'CAN_DELETE')
        self.assertEqual(get_rendered(self.post_1, self.u2), 'CANNOT_DELETE')
        self.assertEqual(get_rendered(self.post_1, self.moderator), 'CAN_DELETE')
        self.assertEqual(get_rendered(self.post_1, self.superuser), 'CAN_DELETE')
