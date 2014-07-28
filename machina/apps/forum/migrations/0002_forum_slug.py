# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='forum',
            name='slug',
            field=models.SlugField(default='gen-forum-slug', max_length=255, verbose_name='Slug'),
            preserve_default=False,
        ),
    ]
