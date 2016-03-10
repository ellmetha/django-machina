# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from faker import Factory as FakerFactory
import pytest

from machina.apps.forum.models import Forum
from machina.core.shortcuts import get_object_or_none
from machina.test.factories import create_forum

faker = FakerFactory.create()


@pytest.mark.django_db
class TestCoreShortcuts(object):
    @pytest.fixture(autouse=True)
    def setup(self):
        self.forum = create_forum()

    def test_can_get_an_object_or_none(self):
        # Setup
        forum_pk = self.forum.pk
        # Run
        forum = get_object_or_none(Forum, pk=forum_pk)
        unknown_forum = get_object_or_none(Forum, pk=10000)
        # Check
        assert self.forum.pk == forum.pk
        assert unknown_forum is None
