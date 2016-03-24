# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('actions', '0003_auto_20150616_1206'),
    ]

    operations = [
        migrations.AlterField(
            model_name='action',
            name='subtype',
            field=models.CharField(default='', max_length=40),
            preserve_default=True,
        ),
    ]
