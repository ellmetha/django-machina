# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='forum',
            options={'ordering': ['tree_id', 'lft'], 'verbose_name': 'Forum', 'verbose_name_plural': 'Forums', 'permissions': [('can_see_forum', 'Can see forum'), ('can_read_forum', 'Can read forum'), ('can_start_new_topics', 'Can start new topics'), ('can_reply_to_topics', 'Can reply to topics'), ('can_post_announcements', 'Can post announcements'), ('can_post_stickies', 'Can post stickies'), ('can_delete_own_posts', 'Can delete own posts'), ('can_edit_own_posts', 'Can edit own posts'), ('can_post_without_approval', 'Can post without approval'), ('can_create_poll', 'Can create poll'), ('can_vote_in_polls', 'Can vote in polls'), ('can_attach_file', 'Can attach file'), ('can_download_file', 'Can download file'), ('can_close_topics', 'Can close topics'), ('can_move_topics', 'Can move topics'), ('can_edit_posts', 'Can edit posts'), ('can_delete_posts', 'Can delete posts'), ('can_move_posts', 'Can move posts'), ('can_approve_posts', 'Can approve posts')]},
        ),
    ]
