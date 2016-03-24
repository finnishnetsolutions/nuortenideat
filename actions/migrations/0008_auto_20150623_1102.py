# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('actions', '0007_auto_20150619_1601'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sentemails',
            name='notification',
            field=models.ForeignKey(related_name='sent_emails', to='actions.Notification', null=True),
            preserve_default=True,
        ),
    ]
