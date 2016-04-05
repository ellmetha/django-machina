# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings
from django.test.utils import override_settings
import pytest

from machina.core.db.models import get_model
from machina.core.loading import AppNotFoundError
from machina.core.loading import ClassNotFoundError
from machina.core.loading import get_class
from machina.core.loading import get_classes


class TestClassLoadingFunctions(object):
    def test_can_load_a_single_class(self):
        # Run & check
        LastTopicsFeed = get_class('forum_feeds.feeds', 'LastTopicsFeed')  # noqa
        assert 'machina.apps.forum_feeds.feeds' == LastTopicsFeed.__module__

    def test_can_load_many_classes(self):
        # Run & check
        PostForm, TopicForm = get_classes('forum_conversation.forms', ['PostForm', 'TopicForm', ])
        assert 'machina.apps.forum_conversation.forms' == PostForm.__module__
        assert 'machina.apps.forum_conversation.forms' == TopicForm.__module__

    def test_raises_if_the_module_label_is_incorrect(self):
        # Run & check
        with pytest.raises(AppNotFoundError):
            get_class('foo.bar', 'Forum')

    def test_raises_if_the_class_name_is_incorrect(self):
        # Run & check
        with pytest.raises(ClassNotFoundError):
            get_class('forum.models', 'Foo')

    def test_raise_importerror_if_app_raises_importerror(self):
        # Setup
        apps = list(settings.INSTALLED_APPS)
        apps[apps.index('machina.apps.forum')] = 'tests._testsite.importerror_app.forum'
        with override_settings(INSTALLED_APPS=apps):
            with pytest.raises(ImportError):
                get_class('forum.dummy', 'Dummy')

    def test_raise_importerror_if_the_app_is_installed_but_the_module_does_not_exist(self):
        # Run & check
        with pytest.raises(AppNotFoundError):
            get_class('forum.xyz', 'Xyz')


class TestClassLoadingFunctionsWithOverrides(object):
    @pytest.fixture(autouse=True)
    def setup(self):
        self.installed_apps = list(settings.INSTALLED_APPS)
        self.installed_apps[self.installed_apps.index('machina.apps.forum')] = \
            'tests._testsite.apps.forum'

    def test_can_load_a_class_defined_in_a_local_module(self):
        with override_settings(INSTALLED_APPS=self.installed_apps):
            MyNewForumView = get_class('forum.views', 'MyNewForumView')  # noqa
            assert 'tests._testsite.apps.forum.views' == MyNewForumView.__module__

    def test_can_load_a_class_that_is_not_defined_in_the_local_module(self):
        with override_settings(INSTALLED_APPS=self.installed_apps):
            ForumView = get_class('forum.views', 'ForumView')  # noqa
            assert 'machina.apps.forum.views' == ForumView.__module__

    def test_can_load_a_class_from_an_app_module_that_is_not_present_in_the_local_app_module(self):
        with override_settings(INSTALLED_APPS=self.installed_apps):
            ForumAdmin = get_class('forum.admin', 'ForumAdmin')  # noqa
            assert 'machina.apps.forum.admin' == ForumAdmin.__module__

    def test_can_load_classes_from_both_the_local_app_and_the_vanilla_app(self):
        with override_settings(INSTALLED_APPS=self.installed_apps):
            ForumView, MyNewForumView = get_classes(
                'forum.views', ('ForumView', 'MyNewForumView'))
            assert 'machina.apps.forum.views' == ForumView.__module__
            assert 'tests._testsite.apps.forum.views' == MyNewForumView.__module__


class TestModelOverrides(object):
    def test_are_registered_before_vanilla_models(self):
        klass = get_model('forum_conversation', 'Topic')
        assert 'tests._testsite.apps.forum_conversation.models' == klass.__module__
