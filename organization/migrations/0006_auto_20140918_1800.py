# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0005_remove_organization_admins'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='admin',
            name='organization',
        ),
        migrations.RemoveField(
            model_name='admin',
            name='user',
        ),
        migrations.DeleteModel(
            name='Admin',
        ),
    ]
