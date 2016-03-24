# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0002_auto_20140916_1203'),
    ]

    operations = [
        migrations.AddField(
            model_name='idea',
            name='decision_given',
            field=models.DateTimeField(default=None, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='idea',
            name='status',
            field=models.SmallIntegerField(default=0, choices=[(0, 'Luonnos'), (3, 'Julkaistu'), (6, 'Viety eteenp\xe4in'), (9, 'P\xe4\xe4t\xf6s annettu')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='idea',
            name='transferred',
            field=models.DateTimeField(default=None, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='initiative',
            name='published',
            field=models.DateTimeField(default=None, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='initiative',
            name='interaction',
            field=models.SmallIntegerField(default=1, verbose_name='Kuka see tehd\xe4 kannanoton ja vastata gallupeihin?', choices=[(1, 'Kaikki'), (2, 'Rekister\xf6ityneet k\xe4ytt\xe4j\xe4t')]),
        ),
        migrations.AlterField(
            model_name='initiative',
            name='visibility',
            field=models.SmallIntegerField(default=1, verbose_name='n\xe4kyvyys', choices=[(1, 'Luonnos'), (10, 'Julkinen'), (8, 'Arkistoitu')]),
        ),
    ]
