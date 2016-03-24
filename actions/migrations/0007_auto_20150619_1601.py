# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('actions', '0006_auto_20150617_1422'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sentemails',
            name='content_type',
        ),
        migrations.RemoveField(
            model_name='sentemails',
            name='object_id',
        ),
        migrations.AddField(
            model_name='sentemails',
            name='notification',
            field=models.ForeignKey(related_name='sent_emails', default='', to='actions.Notification'),
            preserve_default=False,
        ),
    ]
