# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ForumPermission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('codename', models.CharField(unique=True, max_length=150, verbose_name='Permission codename')),
                ('name', models.CharField(max_length=255, null=True, verbose_name='Permission name', blank=True)),
                ('is_global', models.BooleanField(default=False, help_text='This permission can be granted globally to all the forums', verbose_name='Global permission')),
                ('is_local', models.BooleanField(default=True, help_text='This permission can be granted individually for each forum', verbose_name='Local permission')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Forum permission',
                'verbose_name_plural': 'Forum permissions',
            },
        ),
        migrations.CreateModel(
            name='GroupForumPermission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('has_perm', models.BooleanField(default=True, verbose_name='Has perm')),
                ('forum', models.ForeignKey(verbose_name='Forum', blank=True, to='forum.Forum', null=True)),
                ('group', models.ForeignKey(verbose_name='Group', to='auth.Group')),
                ('permission', models.ForeignKey(verbose_name='Forum permission', to='forum_permission.ForumPermission')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Group forum permission',
                'verbose_name_plural': 'Group forum permissions',
            },
        ),
        migrations.CreateModel(
            name='UserForumPermission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('has_perm', models.BooleanField(default=True, verbose_name='Has perm')),
                ('anonymous_user', models.BooleanField(default=False, verbose_name='Target anonymous user')),
                ('forum', models.ForeignKey(verbose_name='Forum', blank=True, to='forum.Forum', null=True)),
                ('permission', models.ForeignKey(verbose_name='Forum permission', to='forum_permission.ForumPermission')),
                ('user', models.ForeignKey(verbose_name='User', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'User forum permission',
                'verbose_name_plural': 'User forum permissions',
            },
        ),
        migrations.AlterUniqueTogether(
            name='userforumpermission',
            unique_together=set([('permission', 'forum', 'user')]),
        ),
        migrations.AlterUniqueTogether(
            name='groupforumpermission',
            unique_together=set([('permission', 'forum', 'group')]),
        ),
    ]
