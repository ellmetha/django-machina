# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import unicode_literals

# Third party imports
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.models import Group

# Local application / specific library imports
from machina.core.compat import get_user_model
from machina.core.db.models import get_model

ForumPermission = get_model('forum_permission', 'ForumPermission')
GroupForumPermission = get_model('forum_permission', 'GroupForumPermission')
UserForumPermission = get_model('forum_permission', 'UserForumPermission')


class NotUserNorGroup(Exception):
    pass


def assign_perm(perm, user_or_group, forum, has_perm=True):
    user, group = get_identity(user_or_group)
    perm = ForumPermission.objects.get(codename=perm)
    if user:
        return UserForumPermission.objects.create(
            forum=forum,
            permission=perm,
            user=user if not user.is_anonymous() else None,
            anonymous_user=user.is_anonymous(),
            has_perm=has_perm)
    if group:
        return GroupForumPermission.objects.create(
            forum=forum, permission=perm, group=group, has_perm=has_perm)


def remove_perm(perm, user_or_group, forum):
    user, group = get_identity(user_or_group)
    perm = ForumPermission.objects.get(codename=perm)
    if user:
        UserForumPermission.objects.filter(permission=perm, forum=forum, user=user).delete()
    if group:
        GroupForumPermission.objects.filter(permission=perm, forum=forum, group=group).delete()


def get_identity(identity):
    """
    Returns a (user_obj, None) tuple or a (None, group_obj) tuple depending on the considered instance.
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
            '(got {})'.format(identity))
