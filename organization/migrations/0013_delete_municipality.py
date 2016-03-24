# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0012_auto_20141205_1358'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Municipality',
        ),
    ]
