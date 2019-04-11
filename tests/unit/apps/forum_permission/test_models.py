import pytest
from django.core.exceptions import ValidationError

from machina.core.db.models import get_model
from machina.test.factories import ForumPermissionFactory, UserFactory, UserForumPermissionFactory


Forum = get_model('forum', 'Forum')
ForumPermission = get_model('forum_permission', 'ForumPermission')
UserForumPermission = get_model('forum_permission', 'UserForumPermission')


@pytest.mark.django_db
class TestUserForumPermission(object):
    def test_cannot_target_an_anonymous_user_and_a_registered_user(self):
        # Setup
        user = UserFactory.create()
        # Run & check
        with pytest.raises(ValidationError):
            perm = ForumPermissionFactory.create()
            user_perm = UserForumPermissionFactory.build(
                permission=perm, user=user, anonymous_user=True)
            user_perm.clean()
