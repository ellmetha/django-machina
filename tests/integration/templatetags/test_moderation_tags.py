# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.db.models import get_model
from django.template import Context
from django.template.base import Template
from django.test import TestCase
from django.test.client import RequestFactory

# Local application / specific library imports
from machina.core.loading import get_class
from machina.test.factories import create_category_forum
from machina.test.factories import GroupFactory
from machina.test.factories import UserFactory

Forum = get_model('forum', 'Forum')

PermissionHandler = get_class('forum_permission.handler', 'PermissionHandler')
assign_perm = get_class('forum_permission.shortcuts', 'assign_perm')


class TestCanAccessModerationPanelTag(TestCase):
    def setUp(self):
        self.loadstatement = '{% load url from future %}{% load forum_moderation_tags %}'
        self.request_factory = RequestFactory()

        self.u1 = UserFactory.create()
        self.moderators = GroupFactory.create()
        self.moderator = UserFactory.create()
        self.moderator.groups.add(self.moderators)
        self.superuser = UserFactory.create(is_superuser=True)

        # Permission handler
        self.perm_handler = PermissionHandler()

        # Set up a top-level category
        self.top_level_cat = create_category_forum()

        # Assign some permissions
        assign_perm('can_approve_posts', self.moderators, self.top_level_cat)


    def test_can_tell_if_a_user_can_access_the_moderation_panel(self):
        # Setup
        def get_rendered(user):
            request = self.request_factory.get('/')
            request.user = user
            t = Template(self.loadstatement + '{% if request.user|can_access_moderation_panel %}CAN_ACCESS{% else %}CANNOT_ACCESS{% endif %}')
            c = Context({'request': request})
            rendered = t.render(c)

            return rendered

        # Run & check
        self.assertEqual(get_rendered(self.superuser), 'CAN_ACCESS')
        self.assertEqual(get_rendered(self.moderator), 'CAN_ACCESS')
        self.assertEqual(get_rendered(self.u1), 'CANNOT_ACCESS')
