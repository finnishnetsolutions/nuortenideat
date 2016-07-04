# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0026_initiative_commenting_closed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='initiative',
            name='interaction',
            field=models.SmallIntegerField(default=1, verbose_name='Kuka saa kannattaa ja kommentoida?', choices=[(1, 'Kaikki'), (2, 'Rekister\xf6ityneet k\xe4ytt\xe4j\xe4t')]),
            preserve_default=True,
        ),
    ]
