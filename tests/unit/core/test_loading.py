# -*- coding: utf-8 -*-

# Standard library imports
import unittest

# Third party imports
from django import VERSION as DJANGO_VERSION
from django.conf import settings
from django.test import TestCase
from django.test.utils import override_settings

# Local application / specific library imports
from machina.core.db.models import get_model
from machina.core.loading import AppNotFoundError
from machina.core.loading import ClassNotFoundError
from machina.core.loading import get_class
from machina.core.loading import get_classes


class TestClassLoadingFunctions(TestCase):
    def test_can_load_a_single_class(self):
        # Run & check
        LastTopicsFeed = get_class('forum_feeds.feeds', 'LastTopicsFeed')
        self.assertEqual('machina.apps.forum_feeds.feeds', LastTopicsFeed.__module__)

    def test_can_load_many_classes(self):
        # Run & check
        PostForm, TopicForm = get_classes('forum_conversation.forms', ['PostForm', 'TopicForm', ])
        self.assertEqual('machina.apps.forum_conversation.forms', PostForm.__module__)
        self.assertEqual('machina.apps.forum_conversation.forms', TopicForm.__module__)

    def test_raises_if_the_module_label_is_incorrect(self):
        # Run & check
        with self.assertRaises(AppNotFoundError):
            get_classes('foo.bar', 'Forum')

    def test_raises_if_the_class_name_is_incorrect(self):
        # Run & check
        with self.assertRaises(ClassNotFoundError):
            get_classes('forum.models', 'Foo')

    @unittest.skipIf(DJANGO_VERSION >= (1, 7),
        'not required with Django >= 1.7 because dummy installed apps) will be detected by the app registry')
    def test_raises_in_case_of_import_error_with_django_less_than_1_dot_7(self):
        # Run & check
        with override_settings(INSTALLED_APPS=('it.is.bad', )):
            with self.assertRaises(AppNotFoundError):
                get_class('bad', 'Foo')

    def test_raise_importerror_if_app_raises_importerror(self):
        # Setup
        apps = list(settings.INSTALLED_APPS)
        apps[apps.index('machina.apps.forum')] = 'tests._testsite.importerror_app.forum'
        with override_settings(INSTALLED_APPS=apps):
            with self.assertRaises(ImportError):
                get_class('forum.dummy', 'Dummy')


class TestClassLoadingFunctionsWithOverrides(TestCase):
    def setUp(self):
        self.installed_apps = list(settings.INSTALLED_APPS)
        self.installed_apps[self.installed_apps.index('machina.apps.forum')] = 'tests._testsite.apps.forum'

    def test_can_load_a_class_defined_in_a_local_module(self):
        with override_settings(INSTALLED_APPS=self.installed_apps):
            MyNewForumView = get_class('forum.views', 'MyNewForumView')
            self.assertEqual('tests._testsite.apps.forum.views', MyNewForumView.__module__)

    def test_can_load_a_class_that_is_not_defined_in_the_local_module(self):
        with override_settings(INSTALLED_APPS=self.installed_apps):
            ForumView = get_class('forum.views', 'ForumView')
            self.assertEqual('machina.apps.forum.views', ForumView.__module__)

    def test_can_load_a_class_from_an_app_module_that_is_not_present_in_the_local_app_module(self):
        with override_settings(INSTALLED_APPS=self.installed_apps):
            ForumAdmin = get_class('forum.admin', 'ForumAdmin')
            self.assertEqual('machina.apps.forum.admin', ForumAdmin.__module__)

    def test_can_load_classes_from_both_the_local_app_and_the_vanilla_app(self):
        with override_settings(INSTALLED_APPS=self.installed_apps):
            ForumView, MyNewForumView = get_classes(
                'forum.views', ('ForumView', 'MyNewForumView'))
            self.assertEqual('machina.apps.forum.views', ForumView.__module__)
            self.assertEqual('tests._testsite.apps.forum.views', MyNewForumView.__module__)


class TestModelOverrides(TestCase):
    def test_are_registered_before_vanilla_models(self):
        klass = get_model('forum_conversation', 'Topic')
        self.assertEqual('tests._testsite.apps.forum_conversation.models', klass.__module__)
