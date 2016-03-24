# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0006_auto_20140918_1800'),
        ('account', '0007_auto_20140918_1722'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='organizations',
            field=models.ManyToManyField(related_name='admins', to='organization.Organization'),
            preserve_default=True,
        ),
    ]
