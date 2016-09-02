# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('forum_conversation', '0006_post_enable_signature'),
    ]

    operations = [
        migrations.AddField(
            model_name='topic',
            name='dummy',
            field=models.CharField(max_length=128, null=True, blank=True),
            preserve_default=True,
        ),
    ]
