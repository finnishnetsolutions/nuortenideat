# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nkmoderation', '0004_auto_20150121_1532'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contentflag',
            name='status',
            field=models.SmallIntegerField(default=1, verbose_name='tila', choices=[(1, 'ilmoitettu'), (2, 'ilmoitus hyl\xe4tty'), (3, 'ilmoitus hyv\xe4ksytty')]),
        ),
    ]
