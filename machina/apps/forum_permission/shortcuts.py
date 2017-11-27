# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.models import Group

from machina.core.db.models import get_model


ForumPermission = get_model('forum_permission', 'ForumPermission')
GroupForumPermission = get_model('forum_permission', 'GroupForumPermission')
UserForumPermission = get_model('forum_permission', 'UserForumPermission')


class NotUserNorGroup(Exception):
    pass


def assign_perm(perm, user_or_group, forum=None, has_perm=True):
    """
    Assign a permission to a user (anonymous or not) or a group.
    """
    user, group = get_identity(user_or_group)
    perm = ForumPermission.objects.get(codename=perm)
    if user:
        return UserForumPermission.objects.create(
            forum=forum,
            permission=perm,
            user=user if not user.is_anonymous else None,
            anonymous_user=user.is_anonymous,
            has_perm=has_perm)
    if group:
        return GroupForumPermission.objects.create(
            forum=forum, permission=perm, group=group, has_perm=has_perm)


def remove_perm(perm, user_or_group, forum=None):
    """
    Remove a permission to a user (anonymous or not) or a group.
    """
    user, group = get_identity(user_or_group)
    perm = ForumPermission.objects.get(codename=perm)
    if user:
        UserForumPermission.objects.filter(
            forum=forum,
            permission=perm,
            user=user if not user.is_anonymous else None,
            anonymous_user=user.is_anonymous).delete()
    if group:
        GroupForumPermission.objects.filter(
            forum=forum, permission=perm, group=group).delete()


def get_identity(identity):
    """
    Returns a (user_obj, None) tuple or a (None, group_obj) tuple depending on the considered
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
            '(got {})'.format(identity))


def get_anonymous_user_forum_key(user):
    """
    Returns the forum key identifier associated with the considered anonymous user.
    """
    return user.forum_key if isinstance(user, AnonymousUser) and hasattr(user, 'forum_key') \
        else None
