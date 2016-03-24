# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kuaapi', '0005_auto_20141210_1014'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kuainitiativestatus',
            name='status',
            field=models.CharField(max_length=20, choices=[('draft', 'Luonnos'), ('published', 'Julkaistu'), ('sent-to-municipality', 'L\xe4hetetty kuntaan'), ('decision-given', 'P\xe4\xe4t\xf6s annettu')]),
        ),
    ]
