# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from collections import OrderedDict

from django.utils.translation import ugettext_lazy as _


class PermissionConfig(object):
    """ Defines the supported forum permissions.

    This class defines the default configuration of forum permissions. It is used to create the
    related ``ForumPermission`` instances on a syncdb or migrate operation. Moreover the permission
    scopes are used in admin pages to display permission forms in a readable way.

    """

    permissions = [
        # Forums
        {
            'fields': {'codename': 'can_see_forum', 'is_local': True, 'is_global': True, },
            'label': _('Can see forum'),
            'scope': 'forum',
        },
        {
            'fields': {'codename': 'can_read_forum', 'is_local': True, 'is_global': True, },
            'label': _('Can read forum'),
            'scope': 'forum',
        },

        # Topics & posts
        {
            'fields': {'codename': 'can_start_new_topics', 'is_local': True, 'is_global': True, },
            'label': _('Can start new topics'),
            'scope': 'conversation',
        },
        {
            'fields': {'codename': 'can_reply_to_topics', 'is_local': True, 'is_global': True, },
            'label': _('Can reply to topics'),
            'scope': 'conversation',
        },
        {
            'fields': {'codename': 'can_post_announcements', 'is_local': True, 'is_global': True, },
            'label': _('Can post announcements'),
            'scope': 'conversation',
        },
        {
            'fields': {'codename': 'can_post_stickies', 'is_local': True, 'is_global': True, },
            'label': _('Can post stickies'),
            'scope': 'conversation',
        },
        {
            'fields': {'codename': 'can_delete_own_posts', 'is_local': True, 'is_global': True, },
            'label': _('Can delete own posts'),
            'scope': 'conversation',
        },
        {
            'fields': {'codename': 'can_edit_own_posts', 'is_local': True, 'is_global': True, },
            'label': _('Can edit own posts'),
            'scope': 'conversation',
        },
        {
            'fields': {
                'codename': 'can_post_without_approval', 'is_local': True, 'is_global': True, },
            'label': _('Can post without approval'),
            'scope': 'conversation',
        },

        # Polls
        {
            'fields': {'codename': 'can_create_polls', 'is_local': True, 'is_global': True, },
            'label': _('Can create polls'),
            'scope': 'polls',
        },
        {
            'fields': {'codename': 'can_vote_in_polls', 'is_local': True, 'is_global': True, },
            'label': _('Can vote in polls'),
            'scope': 'polls',
        },

        # Attachments
        {
            'fields': {'codename': 'can_attach_file', 'is_local': True, 'is_global': True, },
            'label': _('Can attach file'),
            'scope': 'attachments',
        },
        {
            'fields': {'codename': 'can_download_file', 'is_local': True, 'is_global': True, },
            'label': _('Can download file'),
            'scope': 'attachments',
        },

        # Moderation
        {
            'fields': {'codename': 'can_lock_topics', 'is_local': True, 'is_global': False, },
            'label': _('Can lock topics'),
            'scope': 'moderation',
        },
        {
            'fields': {'codename': 'can_move_topics', 'is_local': True, 'is_global': False, },
            'label': _('Can move topics'),
            'scope': 'moderation',
        },
        {
            'fields': {'codename': 'can_edit_posts', 'is_local': True, 'is_global': False, },
            'label': _('Can edit posts'),
            'scope': 'moderation',
        },
        {
            'fields': {'codename': 'can_delete_posts', 'is_local': True, 'is_global': False, },
            'label': _('Can delete posts'),
            'scope': 'moderation',
        },
        {
            'fields': {'codename': 'can_approve_posts', 'is_local': True, 'is_global': False, },
            'label': _('Can approve posts'),
            'scope': 'moderation',
        },
        {
            'fields': {
                'codename': 'can_reply_to_locked_topics', 'is_local': True, 'is_global': False, },
            'label': _('Can add posts in locked topics'),
            'scope': 'moderation',
        },
    ]

    scopes = list(OrderedDict.fromkeys([p['scope'] for p in permissions]))

    def __getitem__(self, key):
        return self._permissions_dict[key]

    def get(self, key, default=None):
        return self._permissions_dict.get(key, default)

    @property
    def _permissions_dict(self):
        if not hasattr(self, '_permissions_per_codename'):
            self._permissions_per_codename = {p['fields']['codename']: p for p in self.permissions}
        return self._permissions_per_codename
