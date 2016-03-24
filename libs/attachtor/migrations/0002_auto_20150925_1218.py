# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings
import libs.attachtor.models.models


class Migration(migrations.Migration):

    dependencies = [
        ('attachtor', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='upload',
            name='file',
            field=models.FileField(max_length=255, upload_to=libs.attachtor.models.models.unique_path),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='upload',
            name='uploader',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
    ]
