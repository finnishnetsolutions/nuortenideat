# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nkvote', '0003_auto_20141007_1337'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vote',
            old_name='client_identification',
            new_name='client_identifier',
        ),
        migrations.AlterUniqueTogether(
            name='vote',
            unique_together=set([('user', 'content_type', 'object_id')]),
        ),
    ]
