# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import libs.multilingo.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('info', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='topic',
            name='description',
            field=libs.multilingo.models.fields.MultilingualTextField(default='', help_text=None, verbose_name='Sis\xe4lt\xf6'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='topic',
            name='title',
            field=libs.multilingo.models.fields.MultilingualTextField(default='', help_text=None, max_length=255, verbose_name='Otsikko'),
            preserve_default=True,
        ),
    ]
