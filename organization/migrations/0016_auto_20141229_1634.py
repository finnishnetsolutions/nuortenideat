# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import libs.attachtor.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0015_auto_20141219_1139'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='search_text',
            field=models.TextField(default=None, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='organization',
            name='description',
            field=libs.attachtor.models.fields.RedactorAttachtorField(default='', verbose_name='kuvaus', blank=True),
            preserve_default=True,
        ),
    ]
