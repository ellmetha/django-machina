"""
    Forum permission shortcuts
    ==========================

    This module defines shortcut functions allowing to easily perform permission checks and to
    assign or remove granted permissions.

"""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser, Group

from machina.core.db.models import get_model


ForumPermission = get_model('forum_permission', 'ForumPermission')
GroupForumPermission = get_model('forum_permission', 'GroupForumPermission')
UserForumPermission = get_model('forum_permission', 'UserForumPermission')

ALL_AUTHENTICATED_USERS = object()  # object to check against if all authenticated users are meant


class NotUserNorGroup(Exception):
    pass


def assign_perm(perm, object, forum=None, has_perm=True):
    """ Assigns a permission to a user (anonymous, specific or all authenticated) or a group.
    object can be either: a user object (specific or anonymous)
                          a group object
                          the ALL_AUTHENTICATED_USERS object for all authenticated users
    """
    perm = ForumPermission.objects.get(codename=perm)

    if object is ALL_AUTHENTICATED_USERS:
        return UserForumPermission.objects.create(
            forum=forum,
            permission=perm,
            user=None,
            anonymous_user=False,
            authenticated_user=True,
            has_perm=has_perm,
        )
    else:
        user, group = get_identity(object)

        if user:
            return UserForumPermission.objects.create(
                forum=forum,
                permission=perm,
                user=user if not user.is_anonymous else None,
                anonymous_user=user.is_anonymous,
                authenticated_user=False,
                has_perm=has_perm,
            )
        if group:
            return GroupForumPermission.objects.create(
                forum=forum, permission=perm, group=group, has_perm=has_perm,
            )


def remove_perm(perm, object, forum=None):
    """ Remove a permission to a user (anonymous, specific or all authenticated) or a group.
    object can be either: a user object (specific or anonymous)
                          a group object
                          the ALL_AUTHENTICATED_USERS object for all authenticated users
    """
    perm = ForumPermission.objects.get(codename=perm)

    if object is ALL_AUTHENTICATED_USERS:
        return UserForumPermission.objects.filter(
            forum=forum,
            permission=perm,
            user=None,
            anonymous_user=False,
            authenticated_user=True,
        ).delete()
    else:
        user, group = get_identity(object)
        if user:
            UserForumPermission.objects.filter(
                forum=forum,
                permission=perm,
                user=user if not user.is_anonymous else None,
                anonymous_user=user.is_anonymous,
                authenticated_user=False,
            ).delete()
        if group:
            GroupForumPermission.objects.filter(forum=forum, permission=perm, group=group).delete()


def get_identity(identity):
    """ Returns a (user_obj, None) tuple or a (None, group_obj) tuple depending on the considered
        instance.
    """
    if isinstance(identity, AnonymousUser):
        return identity, None

    if isinstance(identity, get_user_model()):
        return identity, None
    elif isinstance(identity, Group):
        return None, identity
    else:  # pragma: no cover
        raise NotUserNorGroup(
            'User/AnonymousUser or Group instance is required '
            '(got {})'.format(identity),
        )


def get_anonymous_user_forum_key(user):
    """ Returns the forum key identifier associated with the considered anonymous user. """
    return (
        user.forum_key if isinstance(user, AnonymousUser) and hasattr(user, 'forum_key')
        else None
    )
