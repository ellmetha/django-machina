# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.core.urlresolvers import reverse
from django.db.models import get_model
from faker import Factory as FakerFactory
from guardian.shortcuts import assign_perm

# Local application / specific library imports
from machina.core.loading import get_class
from machina.test.factories import create_category_forum
from machina.test.factories import create_forum
from machina.test.factories import create_topic
from machina.test.factories import ForumReadTrackFactory
from machina.test.factories import GroupFactory
from machina.test.factories import PostFactory
from machina.test.factories import UserFactory
from machina.test.testcases import BaseClientTestCase

faker = FakerFactory.create()

Forum = get_model('forum', 'Forum')

PermissionHandler = get_class('forum_permission.handler', 'PermissionHandler')
TrackingHandler = get_class('forum_tracking.handler', 'TrackingHandler')


class TestMarkForumsReadView(BaseClientTestCase):
    def setUp(self):
        super(TestMarkForumsReadView, self).setUp()

        # Add some users
        self.u1 = UserFactory.create()
        self.u2 = UserFactory.create()
        self.g1 = GroupFactory.create()
        self.u1.groups.add(self.g1)
        self.u2.groups.add(self.g1)
        self.user.groups.add(self.g1)

        # Permission handler
        self.perm_handler = PermissionHandler()

        # Tracking handler
        self.tracks_handler = TrackingHandler()

        self.top_level_cat_1 = create_category_forum()
        self.top_level_cat_2 = create_category_forum()

        self.forum_1 = create_forum(parent=self.top_level_cat_1)
        self.forum_2 = create_forum(parent=self.top_level_cat_1)
        self.forum_2_child_1 = create_forum(parent=self.forum_2)
        self.forum_3 = create_forum(parent=self.top_level_cat_1)

        self.forum_4 = create_forum(parent=self.top_level_cat_2)

        self.topic = create_topic(forum=self.forum_2, poster=self.u1)
        PostFactory.create(topic=self.topic, poster=self.u1)

        # Initially u2 and user read the previously created topic
        ForumReadTrackFactory.create(forum=self.forum_2, user=self.u2)
        ForumReadTrackFactory.create(forum=self.forum_2, user=self.user)

        # Assign some permissions
        assign_perm('can_read_forum', self.g1, self.top_level_cat_1)
        assign_perm('can_read_forum', self.g1, self.top_level_cat_2)
        assign_perm('can_read_forum', self.g1, self.forum_1)
        assign_perm('can_read_forum', self.g1, self.forum_2)
        assign_perm('can_read_forum', self.g1, self.forum_2_child_1)
        assign_perm('can_read_forum', self.g1, self.forum_4)

    def test_browsing_works(self):
        # Setup
        correct_url_1 = reverse('forum-tracking:mark-all-forums-read')
        correct_url_2 = reverse('forum-tracking:mark-subforums-read', kwargs={'pk': self.top_level_cat_1.pk})
        # Run
        response_1 = self.client.get(correct_url_1, follow=True)
        response_2 = self.client.get(correct_url_2, follow=True)
        # Check
        self.assertIsOk(response_1)
        self.assertIsOk(response_2)

    def test_can_mark_all_readable_forums_read(self):
        # Setup
        new_topic = create_topic(forum=self.forum_2, poster=self.u1)
        PostFactory.create(topic=new_topic, poster=self.u1)
        correct_url = reverse('forum-tracking:mark-all-forums-read')
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        self.assertIsOk(response)
        self.assertQuerysetEqual(self.tracks_handler.get_unread_forums(
            Forum.objects.all(), self.user), [])

    def test_can_mark_subforums_read(self):
        # Setup
        new_topic = create_topic(forum=self.forum_2, poster=self.u1)
        PostFactory.create(topic=new_topic, poster=self.u1)
        new_topic = create_topic(forum=self.forum_4, poster=self.u1)
        PostFactory.create(topic=new_topic, poster=self.u1)
        correct_url = reverse('forum-tracking:mark-subforums-read', kwargs={'pk': self.top_level_cat_1.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        self.assertIsOk(response)
        self.assertQuerysetEqual(self.tracks_handler.get_unread_forums(
            self.top_level_cat_1.get_descendants(include_self=True), self.user), [])
        self.assertQuerysetEqual(self.tracks_handler.get_unread_forums(
            Forum.objects.all(), self.user), [self.top_level_cat_2, self.forum_4, ])


class TestMarkTopicsReadView(BaseClientTestCase):
    def setUp(self):
        super(TestMarkTopicsReadView, self).setUp()

        # Add some users
        self.u1 = UserFactory.create()
        self.u2 = UserFactory.create()
        self.g1 = GroupFactory.create()
        self.u1.groups.add(self.g1)
        self.u2.groups.add(self.g1)
        self.user.groups.add(self.g1)

        # Permission handler
        self.perm_handler = PermissionHandler()

        # Tracking handler
        self.tracks_handler = TrackingHandler()

        self.top_level_cat_1 = create_category_forum()
        self.top_level_cat_2 = create_category_forum()

        self.forum_1 = create_forum(parent=self.top_level_cat_1)
        self.forum_2 = create_forum(parent=self.top_level_cat_1)
        self.forum_2_child_1 = create_forum(parent=self.forum_2)
        self.forum_3 = create_forum(parent=self.top_level_cat_1)

        self.forum_4 = create_forum(parent=self.top_level_cat_2)

        self.topic = create_topic(forum=self.forum_2, poster=self.u1)
        PostFactory.create(topic=self.topic, poster=self.u1)

        # Initially u2 and user read the previously created topic
        ForumReadTrackFactory.create(forum=self.forum_2, user=self.u2)
        ForumReadTrackFactory.create(forum=self.forum_2, user=self.user)

        # Assign some permissions
        assign_perm('can_read_forum', self.g1, self.top_level_cat_1)
        assign_perm('can_read_forum', self.g1, self.top_level_cat_2)
        assign_perm('can_read_forum', self.g1, self.forum_1)
        assign_perm('can_read_forum', self.g1, self.forum_2)
        assign_perm('can_read_forum', self.g1, self.forum_2_child_1)
        assign_perm('can_read_forum', self.g1, self.forum_4)

    def test_browsing_works(self):
        # Setup
        correct_url = reverse('forum-tracking:mark-topics-read', kwargs={'pk': self.forum_2.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        self.assertIsOk(response)

    def test_can_mark_forum_topics_read(self):
        # Setup
        new_topic = create_topic(forum=self.forum_4, poster=self.u1)
        PostFactory.create(topic=new_topic, poster=self.u1)
        correct_url = reverse('forum-tracking:mark-topics-read', kwargs={'pk': self.forum_4.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        self.assertIsOk(response)
        self.assertQuerysetEqual(
            self.tracks_handler.get_unread_topics(self.forum_4.topics.all(), self.user),
            [])

    def test_do_not_perform_anything_if_the_user_has_not_the_required_permission(self):
        # Setup
        self.user.groups.clear()
        correct_url = reverse('forum-tracking:mark-topics-read', kwargs={'pk': self.forum_2.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        self.assertIsForbidden(response)


class TestUnreadTopicsView(BaseClientTestCase):
    def setUp(self):
        super(TestUnreadTopicsView, self).setUp()

        # Add some users
        self.u1 = UserFactory.create()
        self.u2 = UserFactory.create()
        self.g1 = GroupFactory.create()
        self.u1.groups.add(self.g1)
        self.u2.groups.add(self.g1)
        self.user.groups.add(self.g1)

        # Permission handler
        self.perm_handler = PermissionHandler()

        # Tracking handler
        self.tracks_handler = TrackingHandler()

        self.top_level_cat_1 = create_category_forum()
        self.top_level_cat_2 = create_category_forum()

        self.forum_1 = create_forum(parent=self.top_level_cat_1)
        self.forum_2 = create_forum(parent=self.top_level_cat_1)
        self.forum_2_child_1 = create_forum(parent=self.forum_2)
        self.forum_3 = create_forum(parent=self.top_level_cat_1)

        self.forum_4 = create_forum(parent=self.top_level_cat_2)

        self.topic = create_topic(forum=self.forum_2, poster=self.u1)
        PostFactory.create(topic=self.topic, poster=self.u1)

        # Initially u2 and user read the previously created topic
        ForumReadTrackFactory.create(forum=self.forum_2, user=self.u2)
        ForumReadTrackFactory.create(forum=self.forum_2, user=self.user)

        # Assign some permissions
        assign_perm('can_read_forum', self.g1, self.top_level_cat_1)
        assign_perm('can_read_forum', self.g1, self.top_level_cat_2)
        assign_perm('can_read_forum', self.g1, self.forum_1)
        assign_perm('can_read_forum', self.g1, self.forum_2)
        assign_perm('can_read_forum', self.g1, self.forum_2_child_1)
        assign_perm('can_read_forum', self.g1, self.forum_4)

    def test_browsing_works(self):
        # Setup
        correct_url = reverse('forum-tracking:unread-topics')
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        self.assertIsOk(response)

    def test_insert_unred_topics_in_context(self):
        # Setup
        new_topic = create_topic(forum=self.forum_4, poster=self.u1)
        PostFactory.create(topic=new_topic, poster=self.u1)
        correct_url = reverse('forum-tracking:unread-topics')
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        self.assertIsOk(response)
        self.assertQuerysetEqual(response.context_data['topics'], [new_topic, ])
