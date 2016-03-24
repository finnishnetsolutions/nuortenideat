# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import libs.multilingo.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('tagging', '0003_delete_tags_add_new_ones'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=libs.multilingo.models.fields.MultilingualTextField(default='', help_text=None, max_length=50, verbose_name='nimi'),
            preserve_default=True,
        ),
    ]
