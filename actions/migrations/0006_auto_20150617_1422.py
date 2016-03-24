# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('actions', '0005_notification_role'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='notification',
            unique_together=set([('action', 'recipient', 'role')]),
        ),
    ]
