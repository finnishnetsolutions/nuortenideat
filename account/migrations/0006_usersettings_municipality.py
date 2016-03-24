# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0004_auto_20140915_1827'),
        ('account', '0005_auto_20140918_1524'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersettings',
            name='municipality',
            field=models.ForeignKey(to='organization.Municipality', null=True),
            preserve_default=True,
        ),
    ]
