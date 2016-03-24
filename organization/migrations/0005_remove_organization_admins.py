# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0004_auto_20140915_1827'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='organization',
            name='admins',
        ),
    ]
