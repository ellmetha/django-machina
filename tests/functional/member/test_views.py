# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import unicode_literals

# Third party imports
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
import pytest

# Local application / specific library imports
from machina.core.db.models import get_model
from machina.core.loading import get_class
from machina.test.factories import create_category_forum
from machina.test.factories import create_forum
from machina.test.factories import create_topic
from machina.test.factories import GroupFactory
from machina.test.factories import PostFactory
from machina.test.factories import UserFactory
from machina.test.testcases import BaseClientTestCase

ForumProfile = get_model('forum_member', 'ForumProfile')

PermissionHandler = get_class('forum_permission.handler', 'PermissionHandler')
assign_perm = get_class('forum_permission.shortcuts', 'assign_perm')


class TestUserTopicsView(BaseClientTestCase):
    @pytest.fixture(autouse=True)
    def setup(self):
        # Add some users
        self.u1 = UserFactory.create()
        self.g1 = GroupFactory.create()
        self.u1.groups.add(self.g1)
        self.user.groups.add(self.g1)

        # Permission handler
        self.perm_handler = PermissionHandler()

        self.top_level_cat_1 = create_category_forum()

        self.forum_1 = create_forum(parent=self.top_level_cat_1)
        self.forum_2 = create_forum(parent=self.top_level_cat_1)
        self.forum_3 = create_forum(parent=self.top_level_cat_1)

        self.topic_1 = create_topic(forum=self.forum_2, poster=self.u1)
        PostFactory.create(topic=self.topic_1, poster=self.u1)
        PostFactory.create(topic=self.topic_1, poster=self.user)

        self.topic_2 = create_topic(forum=self.forum_1, poster=self.user)
        PostFactory.create(topic=self.topic_2, poster=self.user)
        PostFactory.create(topic=self.topic_2, poster=self.u1)

        self.topic_3 = create_topic(forum=self.forum_2, poster=self.u1)
        PostFactory.create(topic=self.topic_3, poster=self.u1)

        self.topic_4 = create_topic(forum=self.forum_2, poster=self.user)
        PostFactory.create(topic=self.topic_4, poster=self.user)

        # Assign some permissions
        assign_perm('can_read_forum', self.g1, self.top_level_cat_1)
        assign_perm('can_read_forum', self.g1, self.forum_1)
        assign_perm('can_read_forum', self.g1, self.forum_2)

    def test_browsing_works(self):
        # Setup
        correct_url = reverse('forum_member:user_topics')
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        assert response.status_code == 200

    def test_insert_only_topics_where_the_considered_user_participated_in_the_context(self):
        # Setup
        correct_url = reverse('forum_member:user_topics')
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        assert response.status_code == 200
        assert list(response.context_data['topics']) == [self.topic_4, self.topic_2, self.topic_1, ]

    def test_does_not_consider_non_approved_posts(self):
        # Setup
        topic_5 = create_topic(forum=self.forum_2, poster=self.user)
        PostFactory.create(topic=topic_5, poster=self.user, approved=False)
        correct_url = reverse('forum_member:user_topics')
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        assert response.status_code == 200
        assert list(response.context_data['topics']) == [self.topic_4, self.topic_2, self.topic_1, ]


class TestForumProfileDetailView(BaseClientTestCase):
    @pytest.fixture(autouse=True)
    def setup(self):
        # Add some users
        self.u1 = UserFactory.create()
        self.g1 = GroupFactory.create()
        self.u1.groups.add(self.g1)
        self.user.groups.add(self.g1)

        # Permission handler
        self.perm_handler = PermissionHandler()

        self.top_level_cat_1 = create_category_forum()

        self.forum_1 = create_forum(parent=self.top_level_cat_1)
        self.forum_2 = create_forum(parent=self.top_level_cat_1)
        self.forum_3 = create_forum(parent=self.top_level_cat_1)

        self.topic_1 = create_topic(forum=self.forum_2, poster=self.u1)
        self.topic_1_post_1 = PostFactory.create(topic=self.topic_1, poster=self.u1)
        self.topic_1_post_2 = PostFactory.create(topic=self.topic_1, poster=self.user)

        self.topic_2 = create_topic(forum=self.forum_1, poster=self.user)
        self.topic_2_post_1 = PostFactory.create(topic=self.topic_2, poster=self.user)
        self.topic_2_post_2 = PostFactory.create(topic=self.topic_2, poster=self.u1)

        self.topic_3 = create_topic(forum=self.forum_2, poster=self.u1)
        self.topic_3_post_1 = PostFactory.create(topic=self.topic_3, poster=self.u1)

        self.topic_4 = create_topic(forum=self.forum_2, poster=self.user)
        self.topic_4_post_1 = PostFactory.create(topic=self.topic_4, poster=self.user)

        # Assign some permissions
        assign_perm('can_read_forum', self.g1, self.top_level_cat_1)
        assign_perm('can_read_forum', self.g1, self.forum_1)
        assign_perm('can_read_forum', self.g1, self.forum_2)

    def test_browsing_works(self):
        # Setup
        correct_url = reverse('forum_member:profile', kwargs={'pk': self.user.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        assert response.status_code == 200

    def test_includes_the_topics_count_in_the_context(self):
        # Setup
        correct_url = reverse('forum_member:profile', kwargs={'pk': self.user.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        assert response.status_code == 200
        assert response.context['topics_count'] == 2

    def test_includes_the_recent_posts_of_the_user_in_the_context(self):
        # Setup
        correct_url = reverse('forum_member:profile', kwargs={'pk': self.user.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        assert response.status_code == 200
        assert list(response.context['recent_posts']) == [
            self.topic_4_post_1,
            self.topic_2_post_1,
            self.topic_1_post_2,
        ]

    def test_recent_posts_are_determined_using_current_user_permissions(self):
        # Setup
        self.user.groups.clear()
        assign_perm('can_read_forum', self.user, self.top_level_cat_1)
        assign_perm('can_read_forum', self.user, self.forum_2)
        correct_url = reverse('forum_member:profile', kwargs={'pk': self.u1.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        assert response.status_code == 200
        assert list(response.context['recent_posts']) == [
            self.topic_3_post_1,
            self.topic_1_post_1,
        ]


class TestForumProfileUpdateView(BaseClientTestCase):
    def test_browsing_works(self):
        # Setup
        correct_url = reverse('forum_member:profile_update')
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        assert response.status_code == 200

    def test_cannot_be_accessed_by_unauthenticated_users(self):
        # Setup
        self.client.logout()
        correct_url = reverse('forum_member:profile_update')
        # Run
        response = self.client.get(correct_url, follow=False)
        # Check
        assert response.status_code == 302

    def test_can_update_forum_profile(self):
        # Setup
        correct_url = reverse('forum_member:profile_update')
        # Run
        with open(settings.MEDIA_ROOT + 'attachment.jpg', 'rb') as upload_file:
            post_data = {
                'signature': '**Test**',
                'avatar': SimpleUploadedFile(upload_file.name, upload_file.read()),
            }
            response = self.client.post(correct_url, post_data, follow=False)
        # Check
        assert response.status_code == 302
        profile = ForumProfile.objects.get(user=self.user)
        assert profile.signature.raw == '**Test**'
        assert profile.avatar.file is not None
