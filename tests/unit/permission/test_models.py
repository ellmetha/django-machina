# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.exceptions import ValidationError
import pytest

from machina.core.db.models import get_model
from machina.test.factories import ForumPermissionFactory
from machina.test.factories import UserFactory
from machina.test.factories import UserForumPermissionFactory

Forum = get_model('forum', 'Forum')
ForumPermission = get_model('forum_permission', 'ForumPermission')
UserForumPermission = get_model('forum_permission', 'UserForumPermission')


@pytest.mark.django_db
class TestForumPermission(object):
    def test_cannot_be_cleaned_without_local_or_global_flag(self):
        # Run & check
        with pytest.raises(ValidationError):
            perm = ForumPermissionFactory.build(is_local=False, is_global=False)
            perm.clean()


@pytest.mark.django_db
class TestUserForumPermission(object):
    def test_cannot_target_an_anonymous_user_and_a_registered_user(self):
        # Setup
        user = UserFactory.create()
        # Run & check
        with pytest.raises(ValidationError):
            perm = ForumPermissionFactory.create(is_local=True, is_global=True)
            user_perm = UserForumPermissionFactory.build(
                permission=perm, user=user, anonymous_user=True)
            user_perm.clean()

    def test_cannot_be_saved_without_forum_if_the_permission_is_not_global(self):
        # Run & check
        with pytest.raises(ValidationError):
            perm = ForumPermissionFactory.create(is_global=False)
            user_perm = UserForumPermissionFactory.build(
                permission=perm)
            user_perm.clean()
