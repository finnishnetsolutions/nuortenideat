# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nkmessages', '0004_auto_20141215_1652'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='from_moderator',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
