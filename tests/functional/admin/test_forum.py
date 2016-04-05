# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
import pytest

from machina.apps.forum.admin import PickUserForm
from machina.apps.forum_permission.models import ForumPermission
from machina.apps.forum_permission.models import GroupForumPermission
from machina.apps.forum_permission.models import UserForumPermission
from machina.core.db.models import get_model
from machina.test.factories import GroupFactory
from machina.test.factories import GroupForumPermissionFactory
from machina.test.factories import UserFactory
from machina.test.factories import UserForumPermissionFactory
from machina.test.mixins import AdminBaseViewTestMixin
from machina.test.testcases import AdminClientTestCase

Forum = get_model('forum', 'Forum')


class TestForumAdmin(AdminClientTestCase, AdminBaseViewTestMixin):
    model = Forum

    @pytest.fixture(autouse=True)
    def setup(self):
        # Set up a top-level category
        top_level_cat = Forum.objects.create(name='top_level_cat', type=Forum.FORUM_CAT)
        self.top_level_cat = top_level_cat

        # Set up some sub forums
        self.sub_forum_1 = Forum.objects.create(
            name='top_level_forum_1', type=Forum.FORUM_POST, parent=top_level_cat)
        self.sub_forum_2 = Forum.objects.create(
            name='top_level_forum_2', type=Forum.FORUM_POST, parent=top_level_cat)
        self.sub_forum_3 = Forum.objects.create(
            name='top_level_forum_3', type=Forum.FORUM_POST, parent=top_level_cat)

        # Set up a top-level forum
        self.top_level_forum = Forum.objects.create(name='top_level_forum', type=Forum.FORUM_POST)

    def test_can_move_a_forum_upward(self):
        # Setup
        model = self.model
        raw_url = 'admin:{}_{}_move'.format(
            model._meta.app_label, self._get_module_name(model._meta))
        # Run
        url = reverse(raw_url, kwargs={'forum_id': self.top_level_forum.id, 'direction': 'up'})
        response = self.client.get(url)
        moved_forum = Forum.objects.get(id=self.top_level_forum.id)
        # Check
        assert response.status_code == 302
        assert moved_forum.get_previous_sibling() is None
        assert moved_forum.get_next_sibling() == self.top_level_cat

    def test_can_move_a_forum_downward(self):
        # Setup
        model = self.model
        raw_url = 'admin:{}_{}_move'.format(
            model._meta.app_label, self._get_module_name(model._meta))
        # Run
        url = reverse(raw_url, kwargs={'forum_id': self.sub_forum_2.id, 'direction': 'down'})
        response = self.client.get(url)
        moved_forum = Forum.objects.get(id=self.sub_forum_2.id)
        # Check
        assert response.status_code == 302
        assert moved_forum.get_previous_sibling() == self.sub_forum_3
        assert moved_forum.get_next_sibling() is None

    def test_can_not_move_a_forum_with_no_siblings(self):
        # Setup
        model = self.model
        raw_url = 'admin:{}_{}_move'.format(
            model._meta.app_label, self._get_module_name(model._meta))
        # Run
        url = reverse(raw_url, kwargs={'forum_id': self.top_level_cat.id, 'direction': 'up'})
        response = self.client.get(url)
        moved_forum = Forum.objects.get(id=self.top_level_cat.id)
        # Check
        assert response.status_code == 302
        assert moved_forum.get_previous_sibling() is None
        assert moved_forum.get_next_sibling() == self.top_level_forum

    def test_editpermission_index_view_browsing_works(self):
        # Setup
        model = self.model
        raw_url = 'admin:{}_{}_editpermission_index'.format(
            model._meta.app_label, self._get_module_name(model._meta))
        # Run
        url = reverse(raw_url, kwargs={'forum_id': self.top_level_cat.id})
        response = self.client.get(url)
        # Check
        assert response.status_code == 200

    def test_editpermission_index_view_submission_cannot_work_without_data(self):
        # Setup
        model = self.model
        raw_url = 'admin:{}_{}_editpermission_index'.format(
            model._meta.app_label, self._get_module_name(model._meta))
        # Run
        url = reverse(raw_url, kwargs={'forum_id': self.top_level_cat.id})
        response = self.client.post(url)
        # Check
        assert response.status_code == 200
        assert response.context['user_form'].errors is not None

    def test_editpermission_index_view_can_redirect_to_user_permissions_form(self):
        # Setup
        model = self.model
        raw_url = 'admin:{}_{}_editpermission_index'.format(
            model._meta.app_label, self._get_module_name(model._meta))
        # Run
        url = reverse(raw_url, kwargs={'forum_id': self.top_level_cat.id})
        response = self.client.post(url, {'user': self.user.id}, follow=True)
        # Check
        editpermissions_user_raw_url = 'admin:{}_{}_editpermission_user'.format(
            model._meta.app_label, self._get_module_name(model._meta))
        editpermissions_user_url = reverse(editpermissions_user_raw_url, kwargs={
            'forum_id': self.top_level_cat.id, 'user_id': self.user.id})
        assert len(response.redirect_chain)
        last_url, status_code = response.redirect_chain[-1]
        assert editpermissions_user_url in last_url

    def test_editpermission_index_view_can_redirect_to_anonymous_user_permissions_form(self):
        # Setup
        model = self.model
        raw_url = 'admin:{}_{}_editpermission_index'.format(
            model._meta.app_label, self._get_module_name(model._meta))
        # Run
        url = reverse(raw_url, kwargs={'forum_id': self.top_level_cat.id})
        response = self.client.post(url, {'anonymous_user': 1}, follow=True)
        # Check
        editpermissions_anonymous_user_raw_url = 'admin:{}_{}_editpermission_anonymous_user'.format(
            model._meta.app_label, self._get_module_name(model._meta))
        editpermissions_anonymous_user_url = reverse(
            editpermissions_anonymous_user_raw_url, kwargs={'forum_id': self.top_level_cat.id})
        assert len(response.redirect_chain)
        last_url, status_code = response.redirect_chain[-1]
        assert editpermissions_anonymous_user_url in last_url

    def test_editpermission_index_view_can_redirect_to_group_permissions_form(self):
        # Setup
        group = GroupFactory.create()
        model = self.model
        raw_url = 'admin:{}_{}_editpermission_index'.format(
            model._meta.app_label, self._get_module_name(model._meta))
        # Run
        url = reverse(raw_url, kwargs={'forum_id': self.top_level_cat.id})
        response = self.client.post(url, {'group': group.id}, follow=True)
        # Check
        editpermissions_group_raw_url = 'admin:{}_{}_editpermission_group'.format(
            model._meta.app_label, self._get_module_name(model._meta))
        editpermissions_group_url = reverse(editpermissions_group_raw_url, kwargs={
            'forum_id': self.top_level_cat.id, 'group_id': group.id})
        assert len(response.redirect_chain)
        last_url, status_code = response.redirect_chain[-1]
        assert editpermissions_group_url in last_url

    def test_editpermission_index_view_can_copy_permissions_from_another_forum(self):
        # Setup
        group = GroupFactory.create()
        model = self.model

        UserForumPermissionFactory.create(
            permission=ForumPermission.objects.get(codename='can_see_forum'),
            forum=self.sub_forum_1,
            user=self.user, has_perm=False)
        UserForumPermissionFactory.create(
            permission=ForumPermission.objects.get(codename='can_read_forum'),
            forum=self.sub_forum_1,
            user=self.user, has_perm=True)
        UserForumPermissionFactory.create(
            permission=ForumPermission.objects.get(codename='can_start_new_topics'),
            forum=self.sub_forum_1,
            user=self.user, has_perm=False)
        GroupForumPermissionFactory.create(
            permission=ForumPermission.objects.get(codename='can_start_new_topics'),
            forum=self.sub_forum_1,
            group=group, has_perm=False)

        raw_url = 'admin:{}_{}_editpermission_index'.format(
            model._meta.app_label, self._get_module_name(model._meta))
        # Run
        url = reverse(raw_url, kwargs={'forum_id': self.top_level_cat.id})
        response = self.client.post(url, {'forum': self.sub_forum_1.id})
        # Check
        assert response.status_code == 200
        assert UserForumPermission.objects.filter(
            permission__codename='can_see_forum', forum=self.top_level_cat,
            user=self.user, has_perm=False).exists()
        assert UserForumPermission.objects.filter(
            permission__codename='can_read_forum', forum=self.top_level_cat,
            user=self.user, has_perm=True).exists()
        assert UserForumPermission.objects.filter(
            permission__codename='can_start_new_topics', forum=self.top_level_cat,
            user=self.user, has_perm=False).exists()
        assert GroupForumPermission.objects.filter(
            permission__codename='can_start_new_topics', forum=self.top_level_cat,
            group=group, has_perm=False).exists()

    def test_editpermission_form_can_update_user_permissions(self):
        # Setup
        UserForumPermissionFactory.create(
            permission=ForumPermission.objects.get(codename='can_see_forum'),
            forum=self.top_level_cat,
            user=self.user, has_perm=False)
        UserForumPermissionFactory.create(
            permission=ForumPermission.objects.get(codename='can_read_forum'),
            forum=self.top_level_cat,
            user=self.user, has_perm=True)
        UserForumPermissionFactory.create(
            permission=ForumPermission.objects.get(codename='can_start_new_topics'),
            forum=self.top_level_cat,
            user=self.user, has_perm=False)
        model = self.model
        raw_url = 'admin:{}_{}_editpermission_user'.format(
            model._meta.app_label, self._get_module_name(model._meta))
        post_data = {
            'can_see_forum': 'granted',
            'can_read_forum': 'not-granted',
            'can_start_new_topics': 'not-set',
            'can_reply_to_topics': 'not-set',
            'can_post_announcements': 'not-set',
            'can_post_stickies': 'not-set',
            'can_delete_own_posts': 'not-set',
            'can_edit_own_posts': 'not-set',
            'can_post_without_approval': 'not-set',
            'can_create_polls': 'not-set',
            'can_vote_in_polls': 'not-set',
            'can_attach_file': 'not-set',
            'can_download_file': 'not-set',
            'can_lock_topics': 'not-set',
            'can_edit_posts': 'not-set',
            'can_delete_posts': 'not-set',
            'can_approve_posts': 'not-set',
        }
        # Run
        url = reverse(raw_url, kwargs={
            'forum_id': self.top_level_cat.id, 'user_id': self.user.id})
        response = self.client.post(url, post_data)
        # Check
        assert response.status_code == 200
        granted_perm = UserForumPermission.objects.filter(
            permission__codename='can_see_forum', has_perm=True,
            user=self.user, forum=self.top_level_cat)
        assert granted_perm.exists()
        not_granted_perm = UserForumPermission.objects.filter(
            permission__codename='can_read_forum', has_perm=False,
            user=self.user, forum=self.top_level_cat)
        assert not_granted_perm.exists()

    def test_editpermission_form_can_update_anonymous_user_permissions(self):
        # Setup
        model = self.model
        raw_url = 'admin:{}_{}_editpermission_anonymous_user'.format(
            model._meta.app_label, self._get_module_name(model._meta))
        post_data = {
            'can_see_forum': 'granted',
            'can_read_forum': 'not-granted',
            'can_start_new_topics': 'not-set',
            'can_reply_to_topics': 'not-set',
            'can_post_announcements': 'not-set',
            'can_post_stickies': 'not-set',
            'can_delete_own_posts': 'not-set',
            'can_edit_own_posts': 'not-set',
            'can_post_without_approval': 'not-set',
            'can_create_polls': 'not-set',
            'can_vote_in_polls': 'not-set',
            'can_attach_file': 'not-set',
            'can_download_file': 'not-set',
            'can_lock_topics': 'not-set',
            'can_edit_posts': 'not-set',
            'can_delete_posts': 'not-set',
            'can_approve_posts': 'not-set',
        }
        # Run
        url = reverse(raw_url, kwargs={
            'forum_id': self.top_level_cat.id})
        response = self.client.post(url, post_data)
        # Check
        assert response.status_code == 200
        granted_perm = UserForumPermission.objects.filter(
            permission__codename='can_see_forum', has_perm=True,
            anonymous_user=True, forum=self.top_level_cat)
        assert granted_perm.exists()
        not_granted_perm = UserForumPermission.objects.filter(
            permission__codename='can_read_forum', has_perm=False,
            anonymous_user=True, forum=self.top_level_cat)
        assert not_granted_perm.exists()

    def test_editpermission_form_can_update_group_permissions(self):
        # Setup
        group = GroupFactory.create()
        model = self.model
        raw_url = 'admin:{}_{}_editpermission_group'.format(
            model._meta.app_label, self._get_module_name(model._meta))
        post_data = {
            'can_see_forum': 'granted',
            'can_read_forum': 'not-granted',
            'can_start_new_topics': 'not-set',
            'can_reply_to_topics': 'not-set',
            'can_post_announcements': 'not-set',
            'can_post_stickies': 'not-set',
            'can_delete_own_posts': 'not-set',
            'can_edit_own_posts': 'not-set',
            'can_post_without_approval': 'not-set',
            'can_create_polls': 'not-set',
            'can_vote_in_polls': 'not-set',
            'can_attach_file': 'not-set',
            'can_download_file': 'not-set',
            'can_lock_topics': 'not-set',
            'can_edit_posts': 'not-set',
            'can_delete_posts': 'not-set',
            'can_approve_posts': 'not-set',
        }
        # Run
        url = reverse(raw_url, kwargs={
            'forum_id': self.top_level_cat.id, 'group_id': group.id})
        response = self.client.post(url, post_data)
        # Check
        assert response.status_code == 200
        granted_perm = GroupForumPermission.objects.filter(
            permission__codename='can_see_forum', has_perm=True,
            group=group, forum=self.top_level_cat)
        assert granted_perm.exists()
        not_granted_perm = GroupForumPermission.objects.filter(
            permission__codename='can_read_forum', has_perm=False,
            group=group, forum=self.top_level_cat)
        assert not_granted_perm.exists()

    def _get_module_name(self, options):
        try:
            module_name = options.module_name
        except AttributeError:  # pragma: no cover
            module_name = options.model_name
        return module_name


@pytest.mark.django_db
class TestPickUserForm(object):
    def test_cannot_be_validated_if_two_users_are_selected(self):
        # Setup
        user = UserFactory.create()
        site = Site.objects.get_current()
        form_data = {
            'user': user.id,
            'anonymous_user': True,
        }
        # Run
        form = PickUserForm(form_data, admin_site=site)
        # Check
        is_valid = form.is_valid()
        assert not is_valid
