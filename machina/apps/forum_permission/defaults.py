# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import unicode_literals

# Third party imports
# Local application / specific library imports


class PermissionConfig(object):
    permissions = [
        # Forums
        {'codename': 'can_see_forum', 'name': 'Can see forum', 'is_local': True, 'is_global': True},
        {'codename': 'can_read_forum', 'name': 'Can read forum', 'is_local': True, 'is_global': True},
        # Topics & posts
        {'codename': 'can_start_new_topics', 'name': 'Can start new topics', 'is_local': True, 'is_global': True},
        {'codename': 'can_reply_to_topics', 'name': 'Can reply to topics', 'is_local': True, 'is_global': True},
        {'codename': 'can_post_announcements', 'name': 'Can post announcements', 'is_local': True, 'is_global': True},
        {'codename': 'can_post_stickies', 'name': 'Can post stickies', 'is_local': True, 'is_global': True},
        {'codename': 'can_delete_own_posts', 'name': 'Can delete own posts', 'is_local': True, 'is_global': True},
        {'codename': 'can_edit_own_posts', 'name': 'Can edit own posts', 'is_local': True, 'is_global': True},
        {'codename': 'can_post_without_approval', 'name': 'Can post without approval', 'is_local': True, 'is_global': True},
        # Polls
        {'codename': 'can_create_poll', 'name': 'Can create poll', 'is_local': True, 'is_global': True},
        {'codename': 'can_vote_in_polls', 'name': 'Can vote in polls', 'is_local': True, 'is_global': True},
        # Attachments
        {'codename': 'can_attach_file', 'name': 'Can attach file', 'is_local': True, 'is_global': True},
        {'codename': 'can_download_file', 'name': 'Can download file', 'is_local': True, 'is_global': True},
        # Moderation
        {'codename': 'can_close_topics', 'name': 'Can move topics', 'is_local': True, 'is_global': False},
        {'codename': 'can_edit_posts', 'name': 'Can edit posts', 'is_local': True, 'is_global': False},
        {'codename': 'can_delete_posts', 'name': 'Can delete posts', 'is_local': True, 'is_global': False},
        {'codename': 'can_move_posts', 'name': 'Can move posts', 'is_local': True, 'is_global': False},
        {'codename': 'can_approve_posts', 'name': 'Can approve posts', 'is_local': True, 'is_global': False},
    ]
