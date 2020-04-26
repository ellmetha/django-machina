"""
    Forum defailt permissions
    =========================

    This module defines the default permissions that can be configured for a forum applications.

"""

from collections import OrderedDict

from django.utils.translation import gettext_lazy as _


class PermissionConfig:
    """ Defines the supported forum permissions.

    This class defines the default configuration of forum permissions. It is used to create the
    related ``ForumPermission`` instances on a syncdb or migrate operation. Moreover the permission
    scopes are used in admin pages to display permission forms in a readable way.

    """

    permissions = [
        # Forums
        {
            'codename': 'can_see_forum',
            'label': _('Can see forum'),
            'scope': 'forum',
        },
        {
            'codename': 'can_read_forum',
            'label': _('Can read forum'),
            'scope': 'forum',
        },

        # Topics & posts
        {
            'codename': 'can_start_new_topics',
            'label': _('Can start new topics'),
            'scope': 'conversation',
        },
        {
            'codename': 'can_reply_to_topics',
            'label': _('Can reply to topics'),
            'scope': 'conversation',
        },
        {
            'codename': 'can_post_announcements',
            'label': _('Can post announcements'),
            'scope': 'conversation',
        },
        {
            'codename': 'can_post_stickies',
            'label': _('Can post stickies'),
            'scope': 'conversation',
        },
        {
            'codename': 'can_delete_own_posts',
            'label': _('Can delete own posts'),
            'scope': 'conversation',
        },
        {
            'codename': 'can_edit_own_posts',
            'label': _('Can edit own posts'),
            'scope': 'conversation',
        },
        {
            'codename': 'can_post_without_approval',
            'label': _('Can post without approval'),
            'scope': 'conversation',
        },

        # Polls
        {
            'codename': 'can_create_polls',
            'label': _('Can create polls'),
            'scope': 'polls',
        },
        {
            'codename': 'can_vote_in_polls',
            'label': _('Can vote in polls'),
            'scope': 'polls',
        },

        # Attachments
        {
            'codename': 'can_attach_file',
            'label': _('Can attach file'),
            'scope': 'attachments',
        },
        {
            'codename': 'can_download_file',
            'label': _('Can download file'),
            'scope': 'attachments',
        },

        # Moderation
        {
            'codename': 'can_lock_topics',
            'label': _('Can lock topics'),
            'scope': 'moderation',
        },
        {
            'codename': 'can_move_topics',
            'label': _('Can move topics'),
            'scope': 'moderation',
        },
        {
            'codename': 'can_edit_posts',
            'label': _('Can edit posts'),
            'scope': 'moderation',
        },
        {
            'codename': 'can_delete_posts',
            'label': _('Can delete posts'),
            'scope': 'moderation',
        },
        {
            'codename': 'can_approve_posts',
            'label': _('Can approve posts'),
            'scope': 'moderation',
        },
        {
            'codename': 'can_reply_to_locked_topics',
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
            self._permissions_per_codename = {p['codename']: p for p in self.permissions}
        return self._permissions_per_codename
