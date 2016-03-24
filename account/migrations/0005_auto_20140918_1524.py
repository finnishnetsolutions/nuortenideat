# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_default_groups'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersettings',
            name='birth_date',
            field=models.DateField(default=datetime.date(2014, 9, 18), verbose_name='syntym\xe4aika'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='usersettings',
            name='email',
            field=models.EmailField(unique=True, max_length=254, verbose_name='s\xe4hk\xf6posti', blank=True),
        ),
        migrations.AlterField(
            model_name='usersettings',
            name='first_name',
            field=models.CharField(max_length=50, verbose_name='etunimi', blank=True),
        ),
        migrations.AlterField(
            model_name='usersettings',
            name='last_name',
            field=models.CharField(max_length=50, verbose_name='sukunimi', blank=True),
        ),
    ]
