# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('forum', '__first__'),
        ('conversation', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='ForumReadTrack',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mark_time', models.DateTimeField(auto_now=True)),
                ('forum', models.ForeignKey(verbose_name='Forum', to='forum.Forum')),
                ('user', models.ForeignKey(verbose_name='User', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Forum track',
                'verbose_name_plural': 'Forum tracks',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='forumreadtrack',
            unique_together=set([('user', 'forum')]),
        ),
        migrations.CreateModel(
            name='TopicReadTrack',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mark_time', models.DateTimeField(auto_now=True)),
                ('topic', models.ForeignKey(verbose_name='Topic', to='conversation.Topic')),
                ('user', models.ForeignKey(verbose_name='User', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Topic track',
                'verbose_name_plural': 'Topic tracks',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='topicreadtrack',
            unique_together=set([('user', 'topic')]),
        ),
    ]
