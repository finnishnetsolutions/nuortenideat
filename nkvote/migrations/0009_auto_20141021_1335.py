# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('nkvote', '0008_auto_20141020_1400'),
    ]

    operations = [
        migrations.AddField(
            model_name='answer',
            name='submit_date',
            field=models.DateTimeField(default=datetime.date(2014, 10, 21), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='gallup',
            name='opened',
            field=models.DateTimeField(null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='option',
            name='seq_number',
            field=models.PositiveSmallIntegerField(default=1),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='question',
            name='seq_number',
            field=models.PositiveSmallIntegerField(default=1),
            preserve_default=True,
        ),
    ]
