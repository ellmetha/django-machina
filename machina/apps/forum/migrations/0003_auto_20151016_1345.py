# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import machina.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0002_auto_20150725_0512'),
    ]

    operations = [
        migrations.AlterField(
            model_name='forum',
            name='description',
            field=machina.models.fields.MarkupTextField(help_text='Description of the forum. It can make use of a markup language if a markup language is configured for your project (or plain HTML in the opposite case).', no_rendered_field=True, null=True, verbose_name='Description', blank=True),
        ),
    ]
