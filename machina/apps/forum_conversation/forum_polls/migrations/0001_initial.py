# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('forum_conversation', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TopicPoll',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Creation date')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Update date')),
                ('question', models.CharField(max_length=255, verbose_name='Poll question')),
                ('duration', models.PositiveIntegerField(null=True, verbose_name='Poll duration, in days', blank=True)),
                ('max_options', models.PositiveSmallIntegerField(default=1, verbose_name='Maximum number of poll options per user', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)])),
                ('user_changes', models.BooleanField(default=False, verbose_name='Allow vote changes')),
                ('topic', models.OneToOneField(related_name='poll', verbose_name='Topic', to='forum_conversation.Topic', on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ['-updated'],
                'abstract': False,
                'get_latest_by': 'updated',
                'verbose_name': 'Topic poll',
                'verbose_name_plural': 'Topic polls',
            },
        ),
        migrations.CreateModel(
            name='TopicPollOption',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.CharField(max_length=255, verbose_name='Poll option text')),
                ('poll', models.ForeignKey(related_name='options', verbose_name='Poll', to='forum_polls.TopicPoll', on_delete=models.CASCADE)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Topic poll option',
                'verbose_name_plural': 'Topic poll options',
            },
        ),
        migrations.CreateModel(
            name='TopicPollVote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name="Vote's date")),
                ('poll_option', models.ForeignKey(related_name='votes', verbose_name='Poll option', to='forum_polls.TopicPollOption', on_delete=models.CASCADE)),
                ('voter', models.ForeignKey(related_name='poll_votes', verbose_name='Voter', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Topic poll vote',
                'verbose_name_plural': 'Topic poll votes',
            },
        ),
    ]
