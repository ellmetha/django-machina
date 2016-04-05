# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.urlresolvers import reverse
import pytest

from machina.apps.forum.signals import forum_viewed
from machina.core.db.models import get_model
from machina.core.loading import get_class
from machina.test.context_managers import mock_signal_receiver
from machina.test.factories import create_forum
from machina.test.factories import create_link_forum
from machina.test.testcases import BaseClientTestCase

Post = get_model('forum_conversation', 'Post')
Topic = get_model('forum_conversation', 'Topic')

PermissionHandler = get_class('forum_permission.handler', 'PermissionHandler')
assign_perm = get_class('forum_permission.shortcuts', 'assign_perm')
remove_perm = get_class('forum_permission.shortcuts', 'remove_perm')


class TestForumView(BaseClientTestCase):
    @pytest.fixture(autouse=True)
    def setup(self):
        # Permission handler
        self.perm_handler = PermissionHandler()

        # Set up a top-level forum and a link forum
        self.top_level_forum = create_forum()
        self.top_level_link = create_link_forum(link_redirects=True)

        # Assign some permissions
        assign_perm('can_read_forum', self.user, self.top_level_forum)
        assign_perm('can_read_forum', self.user, self.top_level_link)

    def test_browsing_works(self):
        # Setup
        correct_url = reverse('forum:forum', kwargs={
            'slug': self.top_level_forum.slug, 'pk': self.top_level_forum.id})
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        assert response.status_code == 200

    def test_cannot_be_browsed_by_users_who_cannot_read_the_forum(self):
        # Setup
        remove_perm('can_read_forum', self.user, self.top_level_forum)
        correct_url = reverse('forum:forum', kwargs={
            'slug': self.top_level_forum.slug, 'pk': self.top_level_forum.id})
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        assert response.status_code == 403

    def test_triggers_a_viewed_signal(self):
        # Setup
        forum_url = reverse('forum:forum', kwargs={
            'slug': self.top_level_forum.slug, 'pk': self.top_level_forum.id})
        link_url = reverse('forum:forum', kwargs={
            'slug': self.top_level_link.slug, 'pk': self.top_level_link.id})

        # Run & check
        for url in [forum_url, link_url]:
            with mock_signal_receiver(forum_viewed) as receiver:
                self.client.get(url)
                assert receiver.call_count == 1

    def test_redirects_to_the_link_of_a_link_forum(self):
        # Setup
        correct_url = reverse('forum:forum', kwargs={
            'slug': self.top_level_link.slug, 'pk': self.top_level_link.id})
        # Run
        response = self.client.get(correct_url)
        # Check
        assert response.status_code == 302
        assert response['Location'] == self.top_level_link.link

    def test_increases_the_redirects_counter_of_a_link_forum(self):
        # Setup
        correct_url = reverse('forum:forum', kwargs={
            'slug': self.top_level_link.slug, 'pk': self.top_level_link.id})
        initial_redirects_count = self.top_level_link.link_redirects_count
        # Run
        self.client.get(correct_url)
        # Check
        top_level_link = self.top_level_link.__class__._default_manager.get(
            pk=self.top_level_link.pk)
        assert top_level_link.link_redirects_count == initial_redirects_count + 1
