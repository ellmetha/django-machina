# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='ForumGroupObjectPermission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content_object', models.ForeignKey(verbose_name='Forum', to='forum.Forum')),
                ('group', models.ForeignKey(to='auth.Group')),
                ('permission', models.ForeignKey(to='auth.Permission')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Group forum object permission',
                'verbose_name_plural': 'Group forum object permissions',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ForumUserObjectPermission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content_object', models.ForeignKey(verbose_name='Forum', to='forum.Forum')),
                ('permission', models.ForeignKey(to='auth.Permission')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'User forum object permission',
                'verbose_name_plural': 'User forum object permissions',
            },
            bases=(models.Model,),
        ),
    ]
