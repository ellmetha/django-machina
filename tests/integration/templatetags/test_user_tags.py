# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import pytest
from django.template import Context
from django.template.base import Template
from django.test import RequestFactory

from machina.test.factories import UserFactory


@pytest.mark.django_db
class TestGetForumUserName(object):
    @pytest.fixture(autouse=True)
    def setup(self):
        self.loadstatement = '{% load forum_user_tags %}'
        self.request_factory = RequestFactory()
        self.u1 = UserFactory.create()
        self.u1.first_name = "Joe"
        self.u1.last_name = "Average"
        self.u1.save()

    def test_can_render_a_user_name(self):
        # Setup
        def get_rendered(user):
            request = self.request_factory.get('/')
            t = Template(self.loadstatement + '{% get_username user as username%}')
            c = Context({'user': user, 'request': request})
            rendered = t.render(c)

            return c, rendered

        context, rendered = get_rendered(self.u1)
        assert rendered == ''
        assert context['username'] == self.u1.username
