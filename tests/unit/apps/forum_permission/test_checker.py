import pytest

from machina.apps.forum_permission.checker import ForumPermissionChecker
from machina.apps.forum_permission.models import ForumPermission
from machina.apps.forum_permission.shortcuts import (
    ALL_AUTHENTICATED_USERS, assign_perm, remove_perm
)
from machina.conf import settings as machina_settings
from machina.test.factories import GroupFactory, UserFactory, create_forum


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

    def test_knows_that_alluser_permissions_take_precedence_over_alluser_global_permissions(self):
        # Setup
        user = UserFactory.create()
        # Test globally True but forum level False
        assign_perm('can_read_forum', ALL_AUTHENTICATED_USERS, None, has_perm=True)
        assign_perm('can_read_forum', ALL_AUTHENTICATED_USERS, self.forum, has_perm=False)
        # Test globally False but forum level True
        assign_perm('can_edit_own_posts', ALL_AUTHENTICATED_USERS, None, has_perm=False)
        assign_perm('can_edit_own_posts', ALL_AUTHENTICATED_USERS, self.forum, has_perm=True)
        checker = ForumPermissionChecker(user)
        # Run & check
        assert not checker.has_perm('can_read_forum', self.forum)
        assert checker.has_perm('can_edit_own_posts', self.forum)

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

    def test_permissions_returned_for_alluser_when_not_in_group_for_given_forum(self):
        """
        When all_users permission is set, a user that has no own permissions and is not
        in a group that has permissions on the given forum, still has a permission (via all_users)
        on the given forum
        """
        user = UserFactory.create()
        assign_perm('can_read_forum', ALL_AUTHENTICATED_USERS, self.forum, has_perm=True)
        checker = ForumPermissionChecker(user)
        # Run & check
        assert checker.has_perm('can_read_forum', self.forum)

    def test_knows_that_alluser_permissions_take_precedence_over_default_authenticated_permissions(self):  # noqa: E501
        user = UserFactory.create()
        # Negate DEFAULT_AUTHENTICATED_USER_FORUM_PERMISSIONS
        assign_perm('can_see_forum', ALL_AUTHENTICATED_USERS, self.forum, has_perm=False)
        checker = ForumPermissionChecker(user)
        # Run & check
        assert not checker.has_perm('can_see_forum', self.forum)

    def test_knows_that_user_permissions_take_precedence_over_group_permissions(self):
        # Setup
        machina_settings.DEFAULT_AUTHENTICATED_USER_FORUM_PERMISSIONS = []
        user = UserFactory.create()
        group = GroupFactory.create()
        user.groups.add(group)
        # Check on forum level if user permission takes precedence over group permission
        assign_perm('can_read_forum', group, self.forum, has_perm=True)
        assign_perm('can_read_forum', user, self.forum, has_perm=False)
        assign_perm('can_see_forum', group, self.forum, has_perm=False)
        assign_perm('can_see_forum', user, self.forum, has_perm=True)

        # Check on global level if user permission takes precedence over group permission
        assign_perm('can_edit_own_posts', group, None, has_perm=True)
        assign_perm('can_edit_own_posts', user, None, has_perm=False)
        assign_perm('can_delete_own_posts', group, None, has_perm=False)
        assign_perm('can_delete_own_posts', user, None, has_perm=True)

        checker = ForumPermissionChecker(user)
        # Run & check
        assert not checker.has_perm('can_read_forum', self.forum)
        assert checker.has_perm('can_see_forum', self.forum)
        assert not checker.has_perm('can_edit_own_posts', self.forum)
        assert checker.has_perm('can_delete_own_posts', self.forum)

    def test_knows_precedence_of_permissions_is_user_group_allusers(self):
        # Setup
        machina_settings.DEFAULT_AUTHENTICATED_USER_FORUM_PERMISSIONS = []
        user = UserFactory.create()
        group = GroupFactory.create()
        user.groups.add(group)

        # 'res' in the following dict means 'expected result'
        test_list = [
            # Differing user settings, all_auth and group to True
            {'level': 'global', 'all_auth': True, 'group': True, 'user': True, 'res': True},
            {'level': 'global', 'all_auth': True, 'group': True, 'user': 'unset', 'res': True},
            {'level': 'global', 'all_auth': True, 'group': True, 'user': False, 'res': False},
            # Differing user settings, all_auto True, group permission False
            {'level': 'global', 'all_auth': True, 'group': False, 'user': True, 'res': True},
            {'level': 'global', 'all_auth': True, 'group': False, 'user': 'unset', 'res': False},
            {'level': 'global', 'all_auth': True, 'group': False, 'user': False, 'res': False},
            # Differing user settings, all_auth and group on False
            {'level': 'global', 'all_auth': False, 'group': False, 'user': True, 'res': True},
            {'level': 'global', 'all_auth': False, 'group': False, 'user': 'unset', 'res': False},
            {'level': 'global', 'all_auth': False, 'group': False, 'user': False, 'res': False},
            # Differing user settings, all_auth False, group permission True
            {'level': 'global', 'all_auth': False, 'group': True, 'user': True, 'res': True},
            {'level': 'global', 'all_auth': False, 'group': True, 'user': 'unset', 'res': True},
            {'level': 'global', 'all_auth': False, 'group': True, 'user': False, 'res': False},
            # Now on forum level instead of global
            # Differing user settings, all_auth and group to True
            {'level': 'forum', 'all_auth': True, 'group': True, 'user': True, 'res': True},
            {'level': 'forum', 'all_auth': True, 'group': True, 'user': 'unset', 'res': True},
            {'level': 'forum', 'all_auth': True, 'group': True, 'user': False, 'res': False},
            # Differing user settings, all_auto True, group permission False
            {'level': 'forum', 'all_auth': True, 'group': False, 'user': True, 'res': True},
            {'level': 'forum', 'all_auth': True, 'group': False, 'user': 'unset', 'res': False},
            {'level': 'forum', 'all_auth': True, 'group': False, 'user': False, 'res': False},
            # Differing user settings, all_auth and group on False
            {'level': 'forum', 'all_auth': False, 'group': False, 'user': True, 'res': True},
            {'level': 'forum', 'all_auth': False, 'group': False, 'user': 'unset', 'res': False},
            {'level': 'forum', 'all_auth': False, 'group': False, 'user': False, 'res': False},
            # Differing user settings, all_auth False, group permission True
            {'level': 'forum', 'all_auth': False, 'group': True, 'user': True, 'res': True},
            {'level': 'forum', 'all_auth': False, 'group': True, 'user': 'unset', 'res': True},
            {'level': 'forum', 'all_auth': False, 'group': True, 'user': False, 'res': False},
        ]

        # loop over test dict:
        for dct in test_list:
            # set each permission as instructed in the dict
            if dct['level'] == 'global':
                forum_val = None
            else:
                forum_val = self.forum
            assign_perm(
                'can_read_forum',
                ALL_AUTHENTICATED_USERS,
                forum_val,
                has_perm=dct['all_auth']
            )
            assign_perm('can_read_forum', group, forum_val, has_perm=dct['group'])
            if dct['user'] != 'unset':
                assign_perm('can_read_forum', user, forum_val, has_perm=dct['user'])

            checker = ForumPermissionChecker(user)
            # test if value is as the expected value
            assert checker.has_perm('can_read_forum', forum_val) == dct['res']

            # unset the set permissions so the next iteration goes in blankly
            remove_perm('can_read_forum', ALL_AUTHENTICATED_USERS, forum_val)
            remove_perm('can_read_forum', group, forum_val)
            if dct['user'] != 'unset':
                remove_perm('can_read_forum', user, forum_val)

    def test_knows_that_granted_permissions_should_take_precedence_over_the_same_non_granted_permissions(self):  # noqa: E501
        # Setup
        user = UserFactory.create()
        group_all_users = GroupFactory.create()
        group_specific_access = GroupFactory.create()
        user.groups.add(group_all_users)
        user.groups.add(group_specific_access)
        assign_perm('can_read_forum', group_all_users, None)  # global permission
        assign_perm('can_read_forum', group_all_users, self.forum, has_perm=False)
        assign_perm('can_read_forum', group_specific_access, self.forum, has_perm=True)
        checker = ForumPermissionChecker(user)
        # Run & check
        assert checker.has_perm('can_read_forum', self.forum)
