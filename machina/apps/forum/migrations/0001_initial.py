# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import mptt.fields
import machina.models.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Forum',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_active', models.BooleanField(default=True, db_index=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Creation date')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Update date')),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('slug', models.SlugField(max_length=255, verbose_name='Slug')),
                ('description', machina.models.fields.MarkupTextField(no_rendered_field=True, null=True, verbose_name='Description', blank=True)),
                ('image', machina.models.fields.ExtendedImageField(upload_to='machina/forum_images', null=True, verbose_name='Forum image', blank=True)),
                ('link', models.URLField(null=True, verbose_name='Forum link', blank=True)),
                ('link_redirects', models.BooleanField(default=False, help_text='Records the number of times a forum link was clicked', verbose_name='Track link redirects count')),
                ('type', models.PositiveSmallIntegerField(db_index=True, verbose_name='Forum type', choices=[(0, 'Default forum'), (1, 'Category forum'), (2, 'Link forum')])),
                ('posts_count', models.PositiveIntegerField(default=0, verbose_name='Number of posts', editable=False, blank=True)),
                ('topics_count', models.PositiveIntegerField(default=0, verbose_name='Number of topics', editable=False, blank=True)),
                ('link_redirects_count', models.PositiveIntegerField(default=0, verbose_name='Track link redirects count', editable=False, blank=True)),
                ('last_post_on', models.DateTimeField(null=True, verbose_name='Last post added on', blank=True)),
                ('display_sub_forum_list', models.BooleanField(default=True, help_text='Displays this forum on the legend of its parent-forum (sub forums list)', verbose_name='Display in parent-forums legend')),
                ('_description_rendered', models.TextField(null=True, editable=False, blank=True)),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
                ('parent', mptt.fields.TreeForeignKey(related_name='children', verbose_name='Parent', blank=True, to='forum.Forum', null=True)),
            ],
            options={
                'ordering': ['tree_id', 'lft'],
                'abstract': False,
                'verbose_name': 'Forum',
                'verbose_name_plural': 'Forums',
                'permissions': [('can_see_forum', 'Can see forum'), ('can_read_forum', 'Can read forum'), ('can_start_new_topics', 'Can start new topics'), ('can_reply_to_topics', 'Can reply to topics'), ('can_post_announcements', 'Can post announcements'), ('can_post_stickies', 'Can post stickies'), ('can_delete_own_posts', 'Can delete own posts'), ('can_edit_own_posts', 'Can edit own posts'), ('can_post_without_approval', 'Can post without approval'), ('can_create_poll', 'Can create poll'), ('can_vote_in_polls', 'Can vote in polls'), ('can_attach_file', 'Can attach file'), ('can_download_file', 'Can download file'), ('can_close_topics', 'Can close topics'), ('can_move_topics', 'Can move topics'), ('can_edit_posts', 'Can edit posts'), ('can_delete_posts', 'Can delete posts'), ('can_move_posts', 'Can move posts'), ('can_approve_posts', 'Can approve posts')],
            },
        ),
    ]
