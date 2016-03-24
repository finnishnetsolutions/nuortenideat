# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0006_usersettings_municipality'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usersettings',
            name='first_name',
            field=models.CharField(max_length=50, verbose_name='etunimi'),
        ),
        migrations.AlterField(
            model_name='usersettings',
            name='last_name',
            field=models.CharField(max_length=50, verbose_name='sukunimi'),
        ),
        migrations.AlterField(
            model_name='usersettings',
            name='municipality',
            field=models.ForeignKey(verbose_name='kotikunta', to='organization.Municipality', null=True),
        ),
    ]
