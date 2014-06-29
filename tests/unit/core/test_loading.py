# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django import VERSION
from django.test import TestCase
from django.test.utils import override_settings

# Local application / specific library imports
from machina.core.loading import AppNotFoundError
from machina.core.loading import ClassNotFoundError
from machina.core.loading import get_class
from machina.core.loading import get_classes


class TestClassLoadingFunctions(TestCase):
    def test_can_load_a_single_class(self):
        # Run & check
        Forum = get_class('forum.models', 'Forum')
        self.assertEqual('machina.apps.forum.models', Forum.__module__)

    def test_can_load_many_classes(self):
        # Run & check
        Topic, Post = get_classes('conversation.models', ['Topic', 'Post', ])
        self.assertEqual('machina.apps.conversation.models', Topic.__module__)
        self.assertEqual('machina.apps.conversation.models', Post.__module__)

    def test_raises_if_the_module_label_is_incorrect(self):
        # Run & check
        with self.assertRaises(AppNotFoundError):
            get_classes('foo.bar', 'Forum')

    def test_raises_if_the_class_name_is_incorrect(self):
        # Run & check
        with self.assertRaises(ClassNotFoundError):
            get_classes('forum.models', 'Foo')

    def test_raises_in_case_of_import_error_with_django_less_than_1_dot_7(self):
        # Run & check
        if VERSION[:2] < (1, 7):
            # We do not check anything with Django 1.7 or greater because any
            # dummy installed app will be detected by the Django app registry
            with override_settings(INSTALLED_APPS=('it.is.bad', )):
                with self.assertRaises(AppNotFoundError):
                    get_class('bad', 'Foo')
