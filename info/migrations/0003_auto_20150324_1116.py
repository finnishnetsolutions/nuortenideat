# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('info', '0002_auto_20150120_1558'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='topic',
            options={'ordering': ['-date'], 'verbose_name': 'Ajankohtaista', 'verbose_name_plural': 'Ajankohtaiset'},
        ),
    ]
