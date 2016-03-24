# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0014_merge'),
    ]

    operations = [
        migrations.RenameField(
            model_name='usersettings',
            old_name='municipality',
            new_name='old_municipality',
        ),
        migrations.AlterField(
            model_name='usersettings',
            name='old_municipality',
            field=models.ForeignKey(db_constraint=False, null=True, verbose_name='kotikunta', to='organization.Municipality', db_index=False),
        ),
    ]
