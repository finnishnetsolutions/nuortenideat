# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0019_auto_20150611_1629'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notificationoptions',
            name='action_subtype',
            field=models.CharField(max_length=40),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='notificationoptions',
            name='action_type',
            field=models.CharField(max_length=16),
            preserve_default=True,
        ),
    ]
