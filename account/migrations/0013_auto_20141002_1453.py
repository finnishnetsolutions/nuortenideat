# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0012_clientidentifier'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clientidentifier',
            name='ip',
            field=models.GenericIPAddressField(),
        ),
    ]
