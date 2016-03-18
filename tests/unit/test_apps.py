# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from machina import get_apps
from machina import MACHINA_VANILLA_APPS


class TestAppGetter(object):
    def test_can_return_the_vanilla_applications(self):
        # Run & check
        assert get_apps() == MACHINA_VANILLA_APPS

    def test_can_use_overridden_applications(self):
        # Run & check
        apps = get_apps(overrides=['test.forum'])
        assert 'test.forum' in apps

    def test_cannot_use_overridden_applications_with_invalid_names(self):
        # Run & check
        apps = get_apps(overrides=['test.forum_alt'])
        assert 'test.forum_alt' not in apps
