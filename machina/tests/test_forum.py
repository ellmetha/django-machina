# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.core.exceptions import ValidationError
from django.db.models import get_model
from django.test import TestCase

# Local application / specific library imports
from machina.apps.forum.abstract_models import FORUM_TYPES
Forum = get_model('forum', 'Forum')


class ForumTestCase(TestCase):
    def setUp(self):
        # Set up a top-level category
        top_level_cat = Forum.objects.create(name='top_level_cat', type=FORUM_TYPES.forum_cat)
        self.top_level_cat = top_level_cat

        # Set up a top-level forum
        top_level_forum = Forum.objects.create(name='top_level_forum', type=FORUM_TYPES.forum_post)
        self.top_level_forum = top_level_forum

        # Set up a top-level forum link
        top_level_link = Forum.objects.create(name='top_level_link', type=FORUM_TYPES.forum_link)
        self.top_level_link = top_level_link

    def test_forum_margin_level(self):
        """
        Tests that the 'margin_level' property which comes with each forum is twice the level
        associated with it.
        """
        # Run
        sub_level_forum = Forum(parent=self.top_level_forum,
                                name='sub_level_forum', type=FORUM_TYPES.forum_post)
        sub_level_forum.full_clean()
        sub_level_forum.save()
        # Check
        self.assertEqual(self.top_level_forum.margin_level, 0)
        self.assertEqual(sub_level_forum.margin_level, 2)

    def test_forum_link_with_childs_should_raise(self):
        """
        Tests that a forum can not have a forum link as parent and that doing so raises a
        ValidationError exception.
        """
        # Run & check
        for forum_type, _ in FORUM_TYPES:
            with self.assertRaises(ValidationError):
                forum = Forum(parent=self.top_level_link, name='sub_forum', type=forum_type)
                forum.full_clean()
