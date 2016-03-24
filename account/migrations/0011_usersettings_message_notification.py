# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0010_auto_20140922_2007'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersettings',
            name='message_notification',
            field=models.BooleanField(default=True, verbose_name='ilmoitus uusista viesteist\xe4'),
            preserve_default=True,
        ),
    ]
