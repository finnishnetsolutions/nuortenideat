# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0021_additionaldetail_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='additionaldetail',
            name='type',
            field=models.SmallIntegerField(default=0, choices=[(0, 'lis\xe4tieto'), (1, 'P\xc4\xc4T\xd6S')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='idea',
            name='picture_alt_text',
            field=models.CharField(default=None, max_length=255, null=True, verbose_name='kuvan tekstimuotoinen kuvaus (suositeltava)'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='initiative',
            name='interaction',
            field=models.SmallIntegerField(default=1, verbose_name='Kuka saa ottaa kantaa ja vastata gallupeihin?', choices=[(1, 'Kaikki'), (2, 'Rekister\xf6ityneet k\xe4ytt\xe4j\xe4t')]),
            preserve_default=True,
        ),
    ]
