# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from faker import Factory as FakerFactory

from machina.forms.widgets import SelectWithDisabled

faker = FakerFactory.create()


class TestSelectWithDisabled(object):
    def test_can_render_a_single_option(self):
        # Setup
        widget = SelectWithDisabled()
        # Run
        rendered = widget.render_option([], '1', 'Test forum')
        # Check
        assert rendered == '<option value="1">Test forum</option>'

    def test_can_render_a_single_option_that_is_selected(self):
        # Setup
        widget = SelectWithDisabled()
        # Run
        rendered = widget.render_option(['1', ], '1', 'Test forum')
        # Check
        assert rendered == '<option value="1" selected="selected">Test forum</option>'

    def test_can_render_a_single_disabled_option(self):
        # Setup
        widget = SelectWithDisabled()
        # Run
        rendered = widget.render_option([], '1', {'label': 'Test forum', 'disabled': True})
        # Check
        assert rendered == '<option value="1" disabled="disabled">Test forum</option>'
