# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kuaapi', '0003_auto_20141209_1634'),
    ]

    operations = [
        migrations.RenameField(
            model_name='kuainitiative',
            old_name='edit_link',
            new_name='management_url',
        ),
    ]
