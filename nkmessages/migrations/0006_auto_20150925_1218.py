# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nkmessages', '0005_message_from_moderator'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='warning',
            field=models.BooleanField(default=False, verbose_name='Varoitusviesti'),
            preserve_default=True,
        ),
    ]
