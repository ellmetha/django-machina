# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.core.urlresolvers import reverse

# Local application / specific library imports
from machina.core.loading import get_class
from machina.test.factories import create_category_forum
from machina.test.factories import create_forum
from machina.test.factories import create_topic
from machina.test.factories import GroupFactory
from machina.test.factories import PostFactory
from machina.test.factories import UserFactory
from machina.test.testcases import BaseClientTestCase

PermissionHandler = get_class('forum_permission.handler', 'PermissionHandler')
assign_perm = get_class('forum_permission.shortcuts', 'assign_perm')


class TestUserTopicsView(BaseClientTestCase):
    def setUp(self):
        super(TestUserTopicsView, self).setUp()

        # Add some users
        self.u1 = UserFactory.create()
        self.g1 = GroupFactory.create()
        self.u1.groups.add(self.g1)
        self.user.groups.add(self.g1)

        # Permission handler
        self.perm_handler = PermissionHandler()

        self.top_level_cat_1 = create_category_forum()

        self.forum_1 = create_forum(parent=self.top_level_cat_1)
        self.forum_2 = create_forum(parent=self.top_level_cat_1)
        self.forum_3 = create_forum(parent=self.top_level_cat_1)

        self.topic_1 = create_topic(forum=self.forum_2, poster=self.u1)
        PostFactory.create(topic=self.topic_1, poster=self.u1)
        PostFactory.create(topic=self.topic_1, poster=self.user)

        self.topic_2 = create_topic(forum=self.forum_1, poster=self.user)
        PostFactory.create(topic=self.topic_2, poster=self.user)
        PostFactory.create(topic=self.topic_2, poster=self.u1)

        self.topic_3 = create_topic(forum=self.forum_2, poster=self.u1)
        PostFactory.create(topic=self.topic_3, poster=self.u1)

        self.topic_4 = create_topic(forum=self.forum_2, poster=self.user)
        PostFactory.create(topic=self.topic_4, poster=self.user)

        # Assign some permissions
        assign_perm('can_read_forum', self.g1, self.top_level_cat_1)
        assign_perm('can_read_forum', self.g1, self.forum_1)
        assign_perm('can_read_forum', self.g1, self.forum_2)

    def test_browsing_works(self):
        # Setup
        correct_url = reverse('forum-member:user-topics')
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        self.assertIsOk(response)

    def test_insert_only_topics_where_the_considered_user_participated_in_the_context(self):
        # Setup
        correct_url = reverse('forum-member:user-topics')
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        self.assertIsOk(response)
        self.assertQuerysetEqual(
            response.context_data['topics'],
            [self.topic_4, self.topic_2, self.topic_1, ])

    def test_does_not_consider_non_approved_posts(self):
        # Setup
        topic_5 = create_topic(forum=self.forum_2, poster=self.user)
        PostFactory.create(topic=topic_5, poster=self.user, approved=False)
        correct_url = reverse('forum-member:user-topics')
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        self.assertIsOk(response)
        self.assertQuerysetEqual(
            response.context_data['topics'],
            [self.topic_4, self.topic_2, self.topic_1, ])
