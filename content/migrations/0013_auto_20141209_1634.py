# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0012_auto_20141205_1438'),
    ]

    operations = [
        migrations.AlterField(
            model_name='idea',
            name='status',
            field=models.SmallIntegerField(default=0, choices=[(0, 'Luonnos'), (3, 'Julkaistu'), (6, 'Viety eteenp\xe4in'), (9, 'P\xe4\xe4t\xf6s annettu')]),
        ),
    ]
