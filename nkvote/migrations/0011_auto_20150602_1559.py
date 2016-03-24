# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import libs.multilingo.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('nkvote', '0010_auto_20141023_1019'),
    ]

    operations = [
        migrations.AlterField(
            model_name='option',
            name='text',
            field=libs.multilingo.models.fields.MultilingualTextField(default='', help_text=None, verbose_name='vaihtoehto'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='question',
            name='text',
            field=libs.multilingo.models.fields.MultilingualTextField(default='', help_text=None, verbose_name='kysymys'),
            preserve_default=True,
        ),
    ]
