# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0017_new_municipalities'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usersettings',
            name='old_municipality',
        ),
        migrations.AlterField(
            model_name='usersettings',
            name='municipality',
            field=models.ForeignKey(to='fimunicipality.Municipality'),
        ),
    ]
