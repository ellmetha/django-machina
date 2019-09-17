"""
    Forum permission checker
    ========================

    This module defines a ``ForumPermissionChecker`` abstraction that allows to check forum
    permissions on specific forum instances.

"""

from django.contrib.auth import get_user_model
from django.db.models import Q

from machina.conf import settings as machina_settings
from machina.core.db.models import get_model


ForumPermission = get_model('forum_permission', 'ForumPermission')
GroupForumPermission = get_model('forum_permission', 'GroupForumPermission')
UserForumPermission = get_model('forum_permission', 'UserForumPermission')


class ForumPermissionChecker:
    """ The ForumPermissionChecker allows to check forum permissions on Forum instances. """

    def __init__(self, user):
        self.user = user
        self._forum_perms_cache = {}

    def has_perm(self, perm, forum):
        """ Checks if the considered user has given permission for the passed forum. """
        if not self.user.is_anonymous and not self.user.is_active:
            # An inactive user cannot have permissions
            return False
        elif self.user and self.user.is_superuser:
            # The superuser have all permissions
            return True
        return perm in self.get_perms(forum)

    def get_perms(self, forum):
        """ Returns the list of permission codenames of all permissions for the given forum. """
        # An inactive user has no permissions.
        if not self.user.is_anonymous and not self.user.is_active:
            return []

        user_model = get_user_model()
        user_groups_related_name = user_model.groups.field.related_query_name()

        if forum.id not in self._forum_perms_cache:
            if self.user and self.user.is_superuser:
                # The superuser has all the permissions.
                permcodes = list(ForumPermission.objects.values_list('codename', flat=True))
            elif self.user:
                default_auth_forum_perms = (
                    machina_settings.DEFAULT_AUTHENTICATED_USER_FORUM_PERMISSIONS
                )

                user_kwargs_filter = (
                    {'anonymous_user': True} if self.user.is_anonymous
                    else {'user': self.user}
                )

                # Fetches the permissions of the considered user for the given forum.
                user_perms = (
                    UserForumPermission.objects.select_related()
                    .filter(**user_kwargs_filter)
                    .filter(Q(forum__isnull=True) | Q(forum=forum))
                )

                # Computes the list of permissions that are granted for all the forums.
                globally_granted_user_perms = list(
                    filter(lambda p: p.has_perm and p.forum_id is None, user_perms)
                )
                globally_granted_user_permcodes = [
                    p.permission.codename for p in globally_granted_user_perms
                ]
                globally_nongranted_user_perms = list(
                    filter(lambda p: not p.has_perm and p.forum_id is None, user_perms)
                )
                # If the considered user have no global permissions, the permissions defined by the
                # DEFAULT_AUTHENTICATED_USER_FORUM_PERMISSIONS settings are used instead.
                if self.user.is_authenticated and not globally_granted_user_perms:
                    globally_granted_user_permcodes = default_auth_forum_perms

                # Computes the list of permissions that are granted on a per-forum basis.
                per_forum_granted_user_perms = list(
                    filter(lambda p: p.has_perm and p.forum_id is not None, user_perms)
                )
                per_forum_granted_user_permcodes = [
                    p.permission.codename for p in per_forum_granted_user_perms
                ]

                # Computes the list of permissions that are not granted on a per-forum basis.
                per_forum_nongranted_user_perms = list(
                    filter(lambda p: not p.has_perm and p.forum_id is not None, user_perms)
                )
                per_forum_nongranted_user_permcodes = [
                    p.permission.codename for p in per_forum_nongranted_user_perms
                ]

                # Finally computes the list of permission codenames that are
                # granted to the user for the considered forum.
                # We can not do this earlier because
                # globally_granted_user_perms can be from the setting
                # DEFAULT_AUTHENTICATED_USER_FORUM_PERMISSIONS in which case
                # it only contains permission codes and not actual permission
                # objects that we can loop over and check against.
                granted_user_permcodes = [
                    c for c in globally_granted_user_permcodes if
                    c not in per_forum_nongranted_user_permcodes
                ]
                granted_user_permcodes = set(granted_user_permcodes +
                                             per_forum_granted_user_permcodes)

                permcodes = granted_user_permcodes

                # If the user is a registered user, we have to check the permissions of its groups
                # in order to determine the additional permissions they could have.
                if not self.user.is_anonymous:
                    group_perms = (
                        GroupForumPermission.objects.select_related()
                        .filter(**{'group__{}'.format(user_groups_related_name): self.user})
                        .filter(Q(forum__isnull=True) | Q(forum=forum))
                    )

                    # A permission can be non-granted on user-forum level, and that takes
                    # precedence over granted group permissions so we do not add those to the list.
                    per_forum_granted_group_perms = list(
                        filter(lambda p: p.has_perm and p.forum_id is not None and
                               p.permission_id not in
                               [q.permission_id for q in per_forum_nongranted_user_perms],
                               group_perms)
                    )
                    per_forum_granted_group_permcodes = [
                        p.permission.codename for p in per_forum_granted_group_perms
                    ]
                    # A permission can be granted on user-forum level, and that takes precedence
                    # over nongranted group permissions so we do not add those to the list.
                    per_forum_nongranted_group_perms = list(
                        filter(lambda p: not p.has_perm and p.forum_id is not None and
                               p.permission_id not in
                               [q.permission_id for q in per_forum_granted_user_perms],
                               group_perms)
                    )

                    # Only get the globally granted group perms that were:
                    # - not set to non-granted on global-user level
                    # - and not set to non-granted on forum-group level
                    globally_granted_group_perms = list(
                        filter(lambda p: p.has_perm and p.forum_id is None and
                               p.permission_id not in
                               [q.permission_id for q in globally_nongranted_user_perms] and
                               p.permission_id not in
                               [y.permission_id for y in per_forum_nongranted_group_perms],
                               group_perms)
                    )
                    globally_granted_group_permcodes = [
                        p.permission.codename for p in globally_granted_group_perms
                    ]

                    granted_group_permcodes = set(globally_granted_group_permcodes +
                                                  per_forum_granted_group_permcodes)

                    # Includes the permissions granted for the user' groups in the initial set of
                    # permission codenames.
                    permcodes |= granted_group_permcodes
            self._forum_perms_cache[forum.id] = permcodes

        return self._forum_perms_cache[forum.id]
