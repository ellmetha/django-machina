# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.core.urlresolvers import reverse
from django.db.models import get_model

# Local application / specific library imports
from machina.apps.forum.abstract_models import FORUM_TYPES
from machina.test.mixins import AdminClientMixin
from machina.test.testcases import AdminClientTestCase
Forum = get_model('forum', 'Forum')


class TestForumAdmin(AdminClientTestCase, AdminClientMixin):
    model = Forum

    def setUp(self):
        super(TestForumAdmin, self).setUp()
        # Set up a top-level category
        top_level_cat = Forum.objects.create(name='top_level_cat', type=FORUM_TYPES.forum_cat)
        self.top_level_cat = top_level_cat

        # Set up some sub forums
        self.sub_forum_1 = Forum.objects.create(name='top_level_forum_1', type=FORUM_TYPES.forum_post, parent=top_level_cat)
        self.sub_forum_2 = Forum.objects.create(name='top_level_forum_2', type=FORUM_TYPES.forum_post, parent=top_level_cat)
        self.sub_forum_3 = Forum.objects.create(name='top_level_forum_3', type=FORUM_TYPES.forum_post, parent=top_level_cat)

        # Set up a top-level forum
        self.top_level_forum = Forum.objects.create(name='top_level_forum', type=FORUM_TYPES.forum_post)

    def test_can_move_a_forum_upward(self):
        # Setup
        model = self.model
        raw_url = 'admin:{}_{}_move'.format(model._meta.app_label, model._meta.module_name)
        # Run
        url = reverse(raw_url, kwargs={'forum_id': self.top_level_forum.id, 'direction': 'up'})
        response = self.client.get(url)
        moved_forum = Forum.objects.get(id=self.top_level_forum.id)
        # Check
        self.assertIsRedirect(response)
        self.assertEqual(moved_forum.get_previous_sibling(), None)
        self.assertEqual(moved_forum.get_next_sibling(), self.top_level_cat)

    def test_can_move_a_forum_downward(self):
        # Setup
        model = self.model
        raw_url = 'admin:{}_{}_move'.format(model._meta.app_label, model._meta.module_name)
        # Run
        url = reverse(raw_url, kwargs={'forum_id': self.sub_forum_2.id, 'direction': 'down'})
        response = self.client.get(url)
        moved_forum = Forum.objects.get(id=self.sub_forum_2.id)
        # Check
        self.assertIsRedirect(response)
        self.assertEqual(moved_forum.get_previous_sibling(), self.sub_forum_3)
        self.assertEqual(moved_forum.get_next_sibling(), None)

    def test_can_not_move_a_forum_with_no_siblings(self):
        # Setup
        model = self.model
        raw_url = 'admin:{}_{}_move'.format(model._meta.app_label, model._meta.module_name)
        # Run
        url = reverse(raw_url, kwargs={'forum_id': self.top_level_cat.id, 'direction': 'up'})
        response = self.client.get(url)
        moved_forum = Forum.objects.get(id=self.top_level_cat.id)
        # Check
        self.assertIsRedirect(response)
        self.assertEqual(moved_forum.get_previous_sibling(), None)
        self.assertEqual(moved_forum.get_next_sibling(), self.top_level_forum)
