# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import image_cropping.fields


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0023_auto_20160427_1046'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersettings',
            name=b'cropping',
            field=image_cropping.fields.ImageRatioField('picture', '220x220', hide_image_field=False, size_warning=True, allow_fullsize=False, free_crop=False, adapt_rotation=False, help_text=None, verbose_name='Profiilikuvan rajaus'),
            preserve_default=True,
        ),
    ]
