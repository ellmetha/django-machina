# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.models import User
from django.template import Context
from django.template.base import Template
from django.test import TestCase
from django.test.client import RequestFactory

# Local application / specific library imports
from machina.conf import settings as machina_settings
from machina.test.factories import UserFactory


class TestIsAnonymousTag(TestCase):
    def setUp(self):
        self.loadstatement = '{% load url from future %}{% load forum_member_tags %}'
        self.request_factory = RequestFactory()
        self.user = UserFactory.create()

    def get_rendered(self, user):
        request = self.request_factory.get('/')
        t = Template(self.loadstatement + '{% if user|is_anonymous %}OK{% else %}NOK{% endif %}')
        c = Context({'user': user, 'request': request})
        rendered = t.render(c)

        return rendered

    def test_can_tell_that_a_registered_user_is_not_anonymous(self):
        # Run & check
        self.assertEqual(self.get_rendered(self.user), 'NOK')

    def test_can_tell_that_a_django_anonymous_user_is_anonymous(self):
        # Run & check
        self.assertEqual(self.get_rendered(AnonymousUser()), 'OK')

    def test_can_tell_that_a_guardian_anonymous_user_is_anonymous(self):
        # Setup
        user = User.objects.get(id=machina_settings.ANONYMOUS_USER_ID)
        # Run & check
        self.assertEqual(self.get_rendered(user), 'OK')
