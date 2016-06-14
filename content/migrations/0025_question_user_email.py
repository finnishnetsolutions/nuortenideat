# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0024_auto_20150925_1218'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='user_email',
            field=models.EmailField(default=None, max_length=254, null=True, blank=True),
            preserve_default=True,
        ),
    ]
