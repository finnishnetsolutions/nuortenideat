# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('help', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='instruction',
            options={'verbose_name': 'Ohje', 'verbose_name_plural': 'Ohjeet'},
        ),
    ]
