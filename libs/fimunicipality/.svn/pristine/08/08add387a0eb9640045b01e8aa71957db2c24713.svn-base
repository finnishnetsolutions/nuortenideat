# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fimunicipality', '0002_auto_20141017_1758'),
    ]

    operations = [
        migrations.AlterField(
            model_name='restructuring',
            name='new_municipality',
            field=models.ForeignKey(related_name='old_municipalities', verbose_name='Former municipalities', to='fimunicipality.Municipality'),
        ),
        migrations.AlterField(
            model_name='restructuring',
            name='old_municipality',
            field=models.ForeignKey(related_name='new_municipalities', verbose_name='New municipalities', to='fimunicipality.Municipality'),
        ),
    ]
