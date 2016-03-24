# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import nuka.models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0023_auto_20150401_1431'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='additionaldetail',
            options={'ordering': ['created', 'pk']},
        ),
        migrations.AlterField(
            model_name='additionaldetail',
            name='detail',
            field=nuka.models.MultilingualRedactorField(default='', help_text=None, verbose_name='lis\xe4tieto'),
            preserve_default=True,
        ),
    ]
