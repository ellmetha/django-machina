# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import machina.models.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ForumProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('avatar', machina.models.fields.ExtendedImageField(upload_to='machina/avatar_images', null=True, verbose_name='Avatar', blank=True)),
                ('signature', machina.models.fields.MarkupTextField(max_length=255, no_rendered_field=True, null=True, verbose_name='Signature', blank=True)),
                ('posts_count', models.PositiveIntegerField(default=0, verbose_name='Total posts', blank=True)),
                ('_signature_rendered', models.TextField(null=True, editable=False, blank=True)),
                ('user', models.OneToOneField(related_name='forum_profile', verbose_name='User', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Forum profile',
                'verbose_name_plural': 'Forum profiles',
            },
        ),
    ]
