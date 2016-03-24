# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0021_auto_20150617_1350'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notificationoptions',
            name='action_subtype',
            field=models.CharField(default='', max_length=100),
            preserve_default=True,
        ),
    ]
