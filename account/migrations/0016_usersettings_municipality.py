# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fimunicipality', '0003_auto_20141020_1401'),
        ('account', '0015_auto_20141205_1230'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersettings',
            name='municipality',
            field=models.ForeignKey(to='fimunicipality.Municipality', null=True),
            preserve_default=True,
        ),
    ]
