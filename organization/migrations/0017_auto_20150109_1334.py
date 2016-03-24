# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import nuka.models


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0016_auto_20141229_1634'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='description',
            field=nuka.models.MultilingualRedactorField(default='', help_text=None, verbose_name='kuvaus', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='organization',
            name='name',
            field=nuka.models.MultilingualTextField(default='', help_text=None, max_length=255, verbose_name='nimi'),
            preserve_default=True,
        ),
    ]
