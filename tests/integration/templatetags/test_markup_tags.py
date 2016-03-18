# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.template import Context
from django.template.base import Template
from django.test.client import RequestFactory
import pytest


class TestRenderedTag(object):
    @pytest.fixture(autouse=True)
    def setup(self):
        self.loadstatement = '{% load forum_markup_tags %}'
        self.request_factory = RequestFactory()

    def test_can_render_a_formatted_text_on_the_fly(self):
        # Setup
        def get_rendered(value):
            request = self.request_factory.get('/')
            t = Template(self.loadstatement + '{{ value|rendered|safe }}')
            c = Context({'value': value, 'request': request})
            rendered = t.render(c)

            return rendered

        assert get_rendered('**This is a test**') == '<p><strong>This is a test</strong></p>'
