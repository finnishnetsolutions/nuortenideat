# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nkmessages', '0006_auto_20150925_1218'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedback',
            name='email',
            field=models.EmailField(max_length=254, verbose_name='s\xe4hk\xf6posti', blank=True),
        ),
        migrations.AlterField(
            model_name='message',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_nkmessages.message_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
    ]
