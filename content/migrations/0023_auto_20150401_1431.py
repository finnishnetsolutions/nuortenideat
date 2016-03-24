# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0022_auto_20150119_1521'),
    ]

    operations = [
        migrations.AlterField(
            model_name='additionaldetail',
            name='type',
            field=models.SmallIntegerField(default=0, choices=[(0, 'lis\xe4tieto'), (1, 'P\xc4\xc4T\xd6S'), (2, 'Viety eteenp\xe4in')]),
            preserve_default=True,
        ),
    ]
