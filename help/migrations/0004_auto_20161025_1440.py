# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('help', '0003_auto_20150122_1352'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='instruction',
            options={'verbose_name': 'ohje', 'verbose_name_plural': 'ohjeet'},
        ),
    ]
