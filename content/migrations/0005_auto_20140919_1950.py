# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import content.models
import imagekit.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0004_auto_20140918_1722'),
    ]

    operations = [
        migrations.AlterField(
            model_name='idea',
            name='picture',
            field=imagekit.models.fields.ProcessedImageField(upload_to=content.models._idea_main_pic_path),
        ),
    ]
