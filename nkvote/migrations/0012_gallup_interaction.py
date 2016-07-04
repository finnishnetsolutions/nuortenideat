# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nkvote', '0011_auto_20150602_1559'),
    ]

    operations = [
        migrations.AddField(
            model_name='gallup',
            name='interaction',
            field=models.SmallIntegerField(default=1, verbose_name='Kuka saa vastata gallupiin?', choices=[(1, 'Kaikki'), (2, 'Rekister\xf6ityneet k\xe4ytt\xe4j\xe4t')]),
            preserve_default=True,
        ),
    ]
