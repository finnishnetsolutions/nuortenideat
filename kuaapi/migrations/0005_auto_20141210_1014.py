# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kuaapi', '0004_auto_20141209_1656'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='kuainitiativestatus',
            unique_together=set([('kua_initiative', 'status')]),
        ),
    ]
