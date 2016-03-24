# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='initiative',
            name='interaction',
            field=models.SmallIntegerField(default=1, verbose_name='Kuka see tehd\xe4 kannanoton ja vastata galluppeihin?', choices=[(1, 'Kaikki'), (2, 'Rekister\xf6ityneet k\xe4ytt\xe4j\xe4t')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='initiative',
            name='owners',
            field=models.ManyToManyField(related_name='initiatives', to=settings.AUTH_USER_MODEL),
        ),
    ]
