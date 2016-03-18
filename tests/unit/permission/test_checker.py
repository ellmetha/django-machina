# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import pytest

from machina.apps.forum_permission.checker import ForumPermissionChecker
from machina.apps.forum_permission.shortcuts import assign_perm
from machina.apps.forum_permission.models import ForumPermission
from machina.conf import settings as machina_settings
from machina.test.factories import create_forum
from machina.test.factories import GroupFactory
from machina.test.factories import UserFactory


@pytest.mark.django_db
class TestForumPermissionChecker(object):
    @pytest.fixture(autouse=True)
    def setup(self):
        self.forum = create_forum()
        machina_settings.DEFAULT_AUTHENTICATED_USER_FORUM_PERMISSIONS = ['can_see_forum', ]

    def teardown_method(self, method):
        machina_settings.DEFAULT_AUTHENTICATED_USER_FORUM_PERMISSIONS = []

    def test_knows_that_a_superuser_has_all_the_permissions(self):
        # Setup
        user = UserFactory.create(is_active=True, is_superuser=True)
        checker = ForumPermissionChecker(user)
        # Run & check
        assert checker.has_perm('can_see_forum', self.forum)
        assert checker.has_perm('can_read_forum', self.forum)
        assert checker.get_perms(self.forum) == \
            list(ForumPermission.objects.values_list('codename', flat=True))

    def test_knows_that_an_inactive_user_has_no_permissions(self):
        # Setup
        user = UserFactory.create(is_active=False)
        checker = ForumPermissionChecker(user)
        # Run & check
        assert not checker.has_perm('can_see_forum', self.forum)
        assert not checker.has_perm('can_read_forum', self.forum)
        assert checker.get_perms(self.forum) == []

    def test_allows_the_use_of_default_permissions(self):
        # Setup
        user = UserFactory.create()
        checker = ForumPermissionChecker(user)
        # Run & check
        assert checker.has_perm('can_see_forum', self.forum)

    def test_can_use_global_permissions(self):
        # Setup
        user = UserFactory.create()
        assign_perm('can_read_forum', user, None)  # global permission
        checker = ForumPermissionChecker(user)
        # Run & check
        assert checker.has_perm('can_read_forum', self.forum)

    def test_knows_that_user_permissions_take_precedence_over_user_global_permissions(self):
        # Setup
        user = UserFactory.create()
        assign_perm('can_read_forum', user, None)  # global permission
        assign_perm('can_read_forum', user, self.forum, has_perm=False)
        checker = ForumPermissionChecker(user)
        # Run & check
        assert not checker.has_perm('can_read_forum', self.forum)

    def test_knows_that_group_permissions_take_precedence_over_group_global_permissions(self):
        # Setup
        user = UserFactory.create()
        group = GroupFactory.create()
        user.groups.add(group)
        assign_perm('can_read_forum', group, None)  # global permission
        assign_perm('can_read_forum', group, self.forum, has_perm=False)
        checker = ForumPermissionChecker(user)
        # Run & check
        assert not checker.has_perm('can_read_forum', self.forum)

    def test_knows_that_user_permissions_take_precedence_over_group_permissions(self):
        # Setup
        user = UserFactory.create()
        group = GroupFactory.create()
        user.groups.add(group)
        assign_perm('can_read_forum', user, self.forum, has_perm=False)
        assign_perm('can_read_forum', group, self.forum, has_perm=True)
        checker = ForumPermissionChecker(user)
        # Run & check
        assert not checker.has_perm('can_read_forum', self.forum)
