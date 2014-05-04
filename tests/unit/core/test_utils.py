# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.test import TestCase
from faker import Factory as FakerFactory

# Local application / specific library imports
from machina.apps.forum.models import Forum
from machina.core.utils import get_object_or_none
from machina.core.utils import refresh
from machina.test.factories import create_forum

faker = FakerFactory.create()


class TestCoreUtils(TestCase):
    def setUp(self):
        self.forum = create_forum()

    def test_can_be_used_to_refresh_a_model_instance(self):
        # Setup
        forum_name = self.forum.name
        new_forum_name = faker.text(max_nb_chars=200)
        # Run
        Forum.objects.all().update(name=new_forum_name)
        # Check
        self.assertEqual(self.forum.name, forum_name)
        forum = refresh(self.forum)
        self.assertEqual(forum.name, new_forum_name)

    def test_can_get_an_object_or_none(self):
        # Setup
        forum_pk = self.forum.pk
        # Run
        forum = get_object_or_none(Forum, pk=forum_pk)
        unknown_forum = get_object_or_none(Forum, pk=10000)
        # Check
        self.assertEqual(self.forum.pk, forum.pk)
        self.assertIsNone(unknown_forum)
