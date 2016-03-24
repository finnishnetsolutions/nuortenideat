# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('actions', '0008_auto_20150623_1102'),
    ]

    operations = [
        migrations.AlterField(
            model_name='action',
            name='subtype',
            field=models.CharField(default='', max_length=100),
            preserve_default=True,
        ),
    ]
