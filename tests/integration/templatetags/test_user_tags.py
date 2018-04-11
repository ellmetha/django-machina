# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import sys

import django
import pytest
from django.conf import settings
from django.template import Context
from django.template.base import Template
from django.test import RequestFactory

import machina.conf.settings
import machina.templatetags.forum_user_tags
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
        def get_rendered(user_id):
            request = self.request_factory.get('/')
            t = Template(self.loadstatement + '{% get_username user_id as username%}')
            c = Context({'user_id': user_id, 'request': request})
            rendered = t.render(c)

            return c, rendered

        context, rendered = get_rendered(self.u1.pk)
        assert rendered == ''
        assert context['username'] == self.u1.username

        # Let's also try to change the setting and see if it still works
        settings.MACHINA_FORUM_USER_DISPLAY = "{{ user.get_full_name }}"
        django.setup()
        if sys.version_info < (3, 4):
            from imp import reload
        else:
            from importlib import reload
        reload(machina.conf.settings)
        reload(machina.templatetags.forum_user_tags)

        context, rendered = get_rendered(self.u1.pk)
        assert rendered == ''
        assert context['username'] == self.u1.get_full_name()
