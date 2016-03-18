# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from collections import OrderedDict


class PermissionConfig(object):
    """
    This class defines the default configuration of forum permissions. It is used
    to create the related ForumPermission instances on a syncdb or migrate operation.
    Moreover the permission scopes are used in admin pages to display permission forms
    in a readable way.
    """
    permissions = [
        # Forums
        {
            'fields': {
                'codename': 'can_see_forum',
                'name': 'Can see forum',
                'is_local': True,
                'is_global': True,
            },
            'scope': 'forum',
        },
        {
            'fields': {
                'codename': 'can_read_forum',
                'name': 'Can read forum',
                'is_local': True,
                'is_global': True,
            },
            'scope': 'forum',
        },
        # Topics & posts
        {
            'fields': {
                'codename': 'can_start_new_topics',
                'name': 'Can start new topics',
                'is_local': True,
                'is_global': True,
            },
            'scope': 'conversation',
        },
        {
            'fields': {
                'codename': 'can_reply_to_topics',
                'name': 'Can reply to topics',
                'is_local': True,
                'is_global': True,
            },
            'scope': 'conversation',
        },
        {
            'fields': {
                'codename': 'can_post_announcements',
                'name': 'Can post announcements',
                'is_local': True,
                'is_global': True,
            },
            'scope': 'conversation',
        },
        {
            'fields': {
                'codename': 'can_post_stickies',
                'name': 'Can post stickies',
                'is_local': True,
                'is_global': True,
            },
            'scope': 'conversation',
        },
        {
            'fields': {
                'codename': 'can_delete_own_posts',
                'name': 'Can delete own posts',
                'is_local': True,
                'is_global': True,
            },
            'scope': 'conversation',
        },
        {
            'fields': {
                'codename': 'can_edit_own_posts',
                'name': 'Can edit own posts',
                'is_local': True,
                'is_global': True,
            },
            'scope': 'conversation',
        },
        {
            'fields': {
                'codename': 'can_post_without_approval',
                'name': 'Can post without approval',
                'is_local': True,
                'is_global': True,
            },
            'scope': 'conversation',
        },
        # Polls
        {
            'fields': {
                'codename': 'can_create_polls',
                'name': 'Can create polls',
                'is_local': True,
                'is_global': True,
            },
            'scope': 'polls',
        },
        {
            'fields': {
                'codename': 'can_vote_in_polls',
                'name': 'Can vote in polls',
                'is_local': True,
                'is_global': True,
            },
            'scope': 'polls',
        },
        # Attachments
        {
            'fields': {
                'codename': 'can_attach_file',
                'name': 'Can attach file',
                'is_local': True,
                'is_global': True,
            },
            'scope': 'attachments',
        },
        {
            'fields': {
                'codename': 'can_download_file',
                'name': 'Can download file',
                'is_local': True,
                'is_global': True,
            },
            'scope': 'attachments',
        },
        # Moderation
        {
            'fields': {
                'codename': 'can_lock_topics',
                'name': 'Can lock topics',
                'is_local': True,
                'is_global': False,
            },
            'scope': 'moderation',
        },
        {
            'fields': {
                'codename': 'can_move_topics',
                'name': 'Can move topics',
                'is_local': True,
                'is_global': False,
            },
            'scope': 'moderation',
        },
        {
            'fields': {
                'codename': 'can_edit_posts',
                'name': 'Can edit posts',
                'is_local': True,
                'is_global': False,
            },
            'scope': 'moderation',
        },
        {
            'fields': {
                'codename': 'can_delete_posts',
                'name': 'Can delete posts',
                'is_local': True,
                'is_global': False,
            },
            'scope': 'moderation',
        },
        {
            'fields': {
                'codename': 'can_approve_posts',
                'name': 'Can approve posts',
                'is_local': True,
                'is_global': False,
            },
            'scope': 'moderation',
        },
        {
            'fields': {
                'codename': 'can_reply_to_locked_topics',
                'name': 'Can add posts in locked topics',
                'is_local': True,
                'is_global': False,
            },
            'scope': 'moderation',
        },
    ]

    scopes = list(OrderedDict.fromkeys([p['scope'] for p in permissions]))
