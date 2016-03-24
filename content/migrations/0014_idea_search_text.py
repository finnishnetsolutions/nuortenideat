# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0013_auto_20141209_1634'),
    ]

    operations = [
        migrations.AddField(
            model_name='idea',
            name='search_text',
            field=models.TextField(default=None, null=True),
            preserve_default=True,
        ),
    ]
