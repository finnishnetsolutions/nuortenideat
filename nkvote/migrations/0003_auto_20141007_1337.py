# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nkvote', '0002_auto_20141007_1300'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vote',
            old_name='target_id',
            new_name='object_id',
        ),
        migrations.AlterUniqueTogether(
            name='vote',
            unique_together=set([('user', 'client_identification', 'content_type', 'object_id')]),
        ),
    ]
