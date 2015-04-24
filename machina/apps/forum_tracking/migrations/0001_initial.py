# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('forum_conversation', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ForumReadTrack',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mark_time', models.DateTimeField(auto_now=True)),
                ('forum', models.ForeignKey(related_name='tracks', verbose_name='Forum', to='forum.Forum')),
                ('user', models.ForeignKey(related_name='forum_tracks', verbose_name='User', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Forum track',
                'verbose_name_plural': 'Forum tracks',
            },
        ),
        migrations.CreateModel(
            name='TopicReadTrack',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mark_time', models.DateTimeField(auto_now=True)),
                ('topic', models.ForeignKey(related_name='tracks', verbose_name='Topic', to='forum_conversation.Topic')),
                ('user', models.ForeignKey(related_name='topic_tracks', verbose_name='User', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Topic track',
                'verbose_name_plural': 'Topic tracks',
            },
        ),
        migrations.AlterUniqueTogether(
            name='topicreadtrack',
            unique_together=set([('user', 'topic')]),
        ),
        migrations.AlterUniqueTogether(
            name='forumreadtrack',
            unique_together=set([('user', 'forum')]),
        ),
    ]
