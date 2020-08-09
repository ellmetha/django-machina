"""
    Forum permission checker
    ========================

    This module defines a ``ForumPermissionChecker`` abstraction that allows to check forum
    permissions on specific forum instances.

"""

from collections import OrderedDict

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

        if forum is None:
            forum_identifier = 'global'
        else:
            forum_identifier = forum.id

        if forum_identifier not in self._forum_perms_cache:
            if self.user and self.user.is_superuser:
                # The superuser has all the permissions.
                permcodes = list(ForumPermission.objects.values_list('codename', flat=True))
            elif self.user:
                perms = self.get_perms_for_forumlist([forum], None)
                permcodes = perms[forum]

            self._forum_perms_cache[forum_identifier] = permcodes

        return self._forum_perms_cache[forum_identifier]

    def get_perms_for_forumlist(self, forums, perm_codenames=None):
        """
            Computes and returns a dictionary of [forum] to (set of permissions) for the user,
            taking into account precendence of permissions:
                - forum > global
                - user > group > all_authenticated_users
            Expects:
            - forums to be a list of forum objects
            - perm_codenames to be a list of permission codes (strings) to look for or None
        """
        globally_granted_all_users_perms = set()
        globally_granted_group_perms, globally_nongranted_group_perms = set(), set()

        user_perms = (
            UserForumPermission.objects.select_related()
            .filter(Q(forum__isnull=True) | Q(forum__in=forums))
        )
        if perm_codenames:
            user_perms = user_perms.filter(permission__codename__in=perm_codenames)

        # Do some additional filtering on (type of) user
        if self.user.is_anonymous:
            user_perms = user_perms.filter(anonymous_user=True)
            all_users_perms = None
            group_perms = None
        else:
            two_types_user_perms = user_perms.filter(Q(authenticated_user=True) | Q(user=self.user))
            all_users_perms = [p for p in two_types_user_perms if p.authenticated_user]
            user_perms = [p for p in two_types_user_perms if p.user]
            # Now get group permissions
            user_model = get_user_model()
            user_groups_related_name = user_model.groups.field.related_query_name()
            group_perms = (
                GroupForumPermission.objects.select_related()
                .filter(**{'group__{}'.format(user_groups_related_name): self.user})
                .filter(Q(forum__isnull=True) | Q(forum__in=forums))
            )
            if perm_codenames:
                group_perms = group_perms.filter(permission__codename__in=perm_codenames)

            # The following 3 lists can already be made outside of the loop over forums
            # But only for non-anonymous users so we do it here
            globally_granted_all_users_perms = list(
                filter(lambda p: p.has_perm and p.forum_id is None, all_users_perms)
            )
            globally_granted_group_perms = list(
                filter(lambda p: p.has_perm and p.forum_id is None, group_perms)
            )
            globally_nongranted_group_perms = list(
                filter(lambda p: not p.has_perm and p.forum_id is None, group_perms)
            )

        # Computes the list of permissions that are non-granted for all the forums.
        globally_nongranted_user_perms = list(
            filter(lambda p: not p.has_perm and p.forum_id is None, user_perms)
        )
        # Computes the list of permissions that are granted for all the forums.
        globally_granted_user_perms = list(
            filter(lambda p: p.has_perm and p.forum_id is None, user_perms)
        )
        globally_granted_user_permcodes = [
            p.permission.codename for p in globally_granted_user_perms
        ]
        # If the considered user has no global permissions, the permissions defined by the
        # DEFAULT_AUTHENTICATED_USER_FORUM_PERMISSIONS settings are used instead.
        if self.user.is_authenticated and not globally_granted_user_permcodes:
            globally_granted_user_permcodes = machina_settings.DEFAULT_AUTHENTICATED_USER_FORUM_PERMISSIONS  # noqa: E501

        forum_to_permissions = OrderedDict()
        for f in forums:
            """
            In every place that we check on f.id we first check if f is actually there
            It might be None because some tests only try global permissions without forum
            """
            # (Re)set these variables for each loop
            permcodes, granted_group_permcodes, granted_all_users_permcodes = set(), set(), set()

            # ########## BLOCK FOR PERMS SPECIFIC TO ONE LOGGED IN USER ###########
            per_forum_granted_user_perms = list(
                filter(lambda p: p.has_perm and f and p.forum_id == f.id, user_perms)
            )
            per_forum_granted_user_permcodes = [
                p.permission.codename for p in per_forum_granted_user_perms
            ]
            per_forum_nongranted_user_perms = list(
                filter(lambda p: not p.has_perm and f and p.forum_id == f.id, user_perms)
            )
            per_forum_nongranted_user_permcodes = [
                p.permission.codename for p in per_forum_nongranted_user_perms
            ]

            per_forum_granted_group_perms = []
            per_forum_nongranted_group_perms = []
            per_forum_nongranted_all_users_permcodes = []
            # ########## BLOCK FOR PERMS SPECIFIC TO GROUPS OF LOGGED IN USER ###########
            # If the user is a registered user, we have to check the permissions of its groups
            # in order to determine the additional permissions they could have.
            if not self.user.is_anonymous:
                if group_perms:
                    # A permission can be non-granted on user-forum level, and that takes
                    # precedence over granted group permissions so we do not add those to the list.
                    per_forum_granted_group_perms = list(
                        filter(lambda p: p.has_perm and f and p.forum_id == f.id and
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
                        filter(lambda p: not p.has_perm and f and p.forum_id == f.id and
                               p.permission_id not in
                               [q.permission_id for q in per_forum_granted_user_perms],
                               group_perms)
                    )

                    # Filter the globally granted group perms to those that were:
                    # - not set to non-granted on global-user level
                    # - and not set to non-granted on forum-group level
                    # - and not set to non-granted on forum-user level
                    globally_granted_group_perms = list(
                        filter(lambda p: p.has_perm and p.forum_id is None and
                               p.permission_id not in
                               [q.permission_id for q in globally_nongranted_user_perms] and
                               p.permission_id not in
                               [y.permission_id for y in per_forum_nongranted_group_perms] and
                               p.permission_id not in
                               [z.permission_id for z in per_forum_nongranted_user_perms],
                               globally_granted_group_perms)
                    )
                    globally_granted_group_permcodes = [
                        p.permission.codename for p in globally_granted_group_perms
                    ]

                    # Filter the globally non granted group perms to those that were:
                    # - not set to granted on global- user level
                    # - and not set to granted on forum-group level
                    # - and not set to granted on forum-user level
                    globally_nongranted_group_perms = list(
                        filter(lambda p: not p.has_perm and p.forum_id is None and
                               p.permission_id not in
                               [q.permission_id for q in globally_granted_user_perms] and
                               p.permission_id not in
                               [y.permission_id for y in per_forum_granted_group_perms] and
                               p.permission_id not in
                               [z.permission_id for z in per_forum_granted_user_perms],
                               globally_nongranted_group_perms)
                    )
                    granted_group_permcodes = set(globally_granted_group_permcodes +
                                                  per_forum_granted_group_permcodes)

                # ######### BLOCK FOR PERMS FOR EVERY LOGGED IN USER ##########
                # A permission can be non-granted on user-forum or group-forum level, and
                # that takes precedence over granted all_users permissions so we do not add
                # those to the list.
                per_forum_granted_all_users_perms = list(
                    filter(lambda p: p.has_perm and f and p.forum_id == f.id and
                           p.permission_id not in
                           [q.permission_id for q in per_forum_nongranted_user_perms] and
                           p.permission_id not in
                           [z.permission_id for z in per_forum_nongranted_group_perms],
                           all_users_perms)
                )
                per_forum_granted_all_users_permcodes = [
                    p.permission.codename for p in per_forum_granted_all_users_perms
                ]

                # A permission can be granted on user-forum or group-forum level, and that takes
                # precedence over nongranted all_user permissions so we do not add those to
                # the list
                per_forum_nongranted_all_users_perms = list(
                    filter(lambda p: not p.has_perm and f and p.forum_id == f.id and
                           p.permission_id not in
                           [q.permission_id for q in per_forum_granted_user_perms] and
                           p.permission_id not in
                           [z.permission_id for z in per_forum_granted_group_perms],
                           all_users_perms)
                )
                per_forum_nongranted_all_users_permcodes = [
                    p.permission.codename for p in per_forum_nongranted_all_users_perms
                ]
                # Filter the globally granted all users perms to those that were:
                # - not set to non-granted on forum-all_user level
                # - and not set to non-granted on global-user level
                # - and not set to non-granted on global-group level
                # - and not set to non-granted on forum-group level
                # - and not set to non-granted on forum-user level
                globally_granted_all_users_perms = list(
                    filter(lambda p: p.has_perm and p.forum_id is None and
                           p.permission_id not in
                           [y.permission_id for y in per_forum_nongranted_all_users_perms] and
                           p.permission_id not in
                           [q.permission_id for q in globally_nongranted_user_perms] and
                           p.permission_id not in
                           [a.permission_id for a in globally_nongranted_group_perms] and
                           p.permission_id not in
                           [x.permission_id for x in per_forum_nongranted_group_perms] and
                           p.permission_id not in
                           [z.permission_id for z in per_forum_nongranted_user_perms],
                           globally_granted_all_users_perms)
                )
                globally_granted_all_users_permcodes = [
                    p.permission.codename for p in globally_granted_all_users_perms
                ]
                granted_all_users_permcodes = set(globally_granted_all_users_permcodes +
                                                  per_forum_granted_all_users_permcodes)

            # Finally computes the list of permission codenames that are
            # granted to the user for the considered forum.
            # We can not do this earlier because
            # globally_granted_user_perms can be from the setting
            # DEFAULT_AUTHENTICATED_USER_FORUM_PERMISSIONS in which case
            # it only contains permission codes and not actual permission
            # objects that we can loop over and check against.
            granted_user_permcodes = [
                c for c in globally_granted_user_permcodes if
                c not in per_forum_nongranted_user_permcodes and
                c not in per_forum_nongranted_all_users_permcodes
            ]
            permcodes = set(granted_user_permcodes +
                            per_forum_granted_user_permcodes)
            # Includes the permissions granted for the user's groups and for all logged
            # in users (that were not overruled by more specific targets) in the initial
            # set of permission codenames.
            forum_to_permissions[f] = permcodes.union(granted_group_permcodes,
                                                      granted_all_users_permcodes)

        return forum_to_permissions
