# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum_conversation', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='anonymous_key',
            field=models.CharField(max_length=100, null=True, verbose_name='Anonymous user forum key', blank=True),
        ),
    ]
