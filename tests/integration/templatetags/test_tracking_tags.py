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
from machina.core.loading import get_class
from machina.test.factories import create_category_forum
from machina.test.factories import create_forum
from machina.test.factories import create_topic
from machina.test.factories import ForumReadTrackFactory
from machina.test.factories import GroupFactory
from machina.test.factories import PostFactory
from machina.test.factories import TopicReadTrackFactory
from machina.test.factories import UserFactory

Forum = get_model('forum', 'Forum')

TrackingHandler = get_class('tracking.handler', 'TrackingHandler')


class BaseTrackingTagsTestCase(TestCase):
    def setUp(self):
        self.loadstatement = '{% load url from future %}{% load tracking_tags %}'
        self.request_factory = RequestFactory()

        # Tracking handler
        self.tracks_handler = TrackingHandler()

        self.g1 = GroupFactory.create()
        self.u1 = UserFactory.create()
        self.u2 = UserFactory.create()
        self.u1.groups.add(self.g1)
        self.u2.groups.add(self.g1)

        # Set up a top-level category
        self.top_level_cat = create_category_forum()

        # Set up some forums
        self.forum_1 = create_forum(parent=self.top_level_cat)
        self.forum_2 = create_forum(parent=self.top_level_cat)

        # Set up some topics and posts
        self.forum_1_topic = create_topic(forum=self.forum_1, poster=self.u1)
        self.forum_2_topic = create_topic(forum=self.forum_2, poster=self.u1)
        self.post_1 = PostFactory.create(topic=self.forum_1_topic, poster=self.u1)
        self.post_2 = PostFactory.create(topic=self.forum_2_topic, poster=self.u1)

        # Assign some permissions
        assign_perm('can_see_forum', self.g1, self.top_level_cat)
        assign_perm('can_read_forum', self.g1, self.top_level_cat)
        assign_perm('can_see_forum', self.g1, self.forum_1)
        assign_perm('can_read_forum', self.g1, self.forum_1)
        assign_perm('can_see_forum', self.g1, self.forum_2)
        assign_perm('can_read_forum', self.g1, self.forum_2)


class TestUnreadForumsTag(BaseTrackingTagsTestCase):
    def test_can_determine_unread_forums(self):
        # Setup
        def get_rendered(forums, user):
            request = self.request_factory.get('/')
            request.user = user
            t = Template(self.loadstatement + '{% get_unread_forums forums request.user as unread_forums %}')
            c = Context({'forums': forums, 'request': request})
            rendered = t.render(c)

            return c, rendered

        # Run & check
        context, rendered = get_rendered(Forum.objects.all(), self.u2)
        self.assertEqual(rendered, '')
        self.assertEqual(set(context['unread_forums']), set([self.top_level_cat, self.forum_1, self.forum_2, ]))

        # forum_1 and forum_2 are now read
        ForumReadTrackFactory.create(forum=self.forum_1, user=self.u2)
        ForumReadTrackFactory.create(forum=self.forum_2, user=self.u2)
        context, rendered = get_rendered(Forum.objects.all(), self.u2)
        self.assertEqual(rendered, '')
        self.assertFalse(len(context['unread_forums']))

        # A new post is created
        PostFactory.create(topic=self.forum_2_topic, poster=self.u1)
        context, rendered = get_rendered(Forum.objects.all(), self.u2)
        self.assertEqual(rendered, '')
        self.assertEqual(set(context['unread_forums']), set([self.forum_2, self.top_level_cat]))


class TestUnreadTopicsTag(BaseTrackingTagsTestCase):
    def test_can_determine_unread_forums(self):
        # Setup
        def get_rendered(topics, user):
            request = self.request_factory.get('/')
            request.user = user
            t = Template(self.loadstatement + '{% get_unread_topics topics request.user as unread_topics %}')
            c = Context({'topics': topics, 'request': request})
            rendered = t.render(c)

            return c, rendered

        # Run & check
        context, rendered = get_rendered(self.forum_2.topics.all(), self.u2)
        self.assertEqual(rendered, '')
        self.assertEqual(set(context['unread_topics']), set(self.forum_2.topics.all()))

        # forum_2 topics are now read
        TopicReadTrackFactory.create(topic=self.forum_2_topic, user=self.u2)
        context, rendered = get_rendered(self.forum_2.topics.all(), self.u2)
        self.assertEqual(rendered, '')
        self.assertFalse(len(context['unread_topics']))

        # A new post is created with a pre-existing topic track
        PostFactory.create(topic=self.forum_2_topic, poster=self.u1)
        context, rendered = get_rendered(self.forum_2.topics.all(), self.u2)
        self.assertEqual(rendered, '')
        self.assertEqual(set(context['unread_topics']), set(self.forum_2.topics.all()))

        # A new post is created with a pre-existing forum track
        ForumReadTrackFactory.create(forum=self.forum_1, user=self.u2)
        PostFactory.create(topic=self.forum_1_topic, poster=self.u1)
        context, rendered = get_rendered(self.forum_1.topics.all(), self.u2)
        self.assertEqual(rendered, '')
        self.assertEqual(set(context['unread_topics']), set(self.forum_1.topics.all()))
