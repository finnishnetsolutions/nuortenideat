# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0029_auto_20160621_1514'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ideasurvey',
            name='interaction',
            field=models.SmallIntegerField(default=1, verbose_name='Kuka saa vastata kyselyyn?', choices=[(1, 'Kaikki'), (2, 'Rekister\xf6ityneet k\xe4ytt\xe4j\xe4t')]),
            preserve_default=True,
        ),
    ]
