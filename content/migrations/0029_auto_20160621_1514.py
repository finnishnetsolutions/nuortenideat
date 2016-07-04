# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0028_ideasurvey'),
    ]

    operations = [
        migrations.AlterField(
            model_name='idea',
            name='picture_alt_text',
            field=models.CharField(default=None, max_length=255, null=True, verbose_name='Mit\xe4 kuvassa on? (kuvaus suositeltava)'),
            preserve_default=True,
        ),
    ]
