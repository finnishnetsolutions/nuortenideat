# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('actions', '0004_auto_20150617_1350'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='role',
            field=models.CharField(default='', max_length=50),
            preserve_default=False,
        ),
    ]
