# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fimunicipality', '0003_auto_20141020_1401'),
        ('organization', '0009_rename_nation'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='municipalities',
            field=models.ManyToManyField(related_name='Kunnat', to='fimunicipality.Municipality'),
            preserve_default=True,
        ),
    ]
