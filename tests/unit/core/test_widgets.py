from faker import Faker

from machina.forms.widgets import SelectWithDisabled


faker = Faker()


class TestSelectWithDisabled(object):
    def test_can_prepare_a_single_option(self):
        # Setup
        widget = SelectWithDisabled()
        # Run
        option = widget.create_option('test', '1', 'Test forum', False, 0)
        # Check
        assert option['name'] == 'test'
        assert option['label'] == 'Test forum'
        assert option['index'] == '0'

    def test_can_prepare_a_single_option_that_is_selected(self):
        # Setup
        widget = SelectWithDisabled()
        # Run
        option = widget.create_option('test', '1', 'Test forum', True, 0)
        # Check
        assert option['name'] == 'test'
        assert option['label'] == 'Test forum'
        assert option['index'] == '0'
        assert option['attrs'] == {'selected': True}

    def test_can_prepare_a_single_disabled_option(self):
        # Setup
        widget = SelectWithDisabled()
        # Run
        option = widget.create_option(
            'test', '1', {'label': 'Test forum', 'disabled': True}, False, 0)
        # Check
        assert option['name'] == 'test'
        assert option['label'] == 'Test forum'
        assert option['index'] == '0'
        assert option['attrs'] == {'disabled': 'disabled'}
