# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import image_cropping.fields


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0017_auto_20150109_1334'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name=b'cropping',
            field=image_cropping.fields.ImageRatioField('picture', '220x220', hide_image_field=False, size_warning=True, allow_fullsize=False, free_crop=False, adapt_rotation=False, help_text=None, verbose_name='Profiilikuvan rajaus'),
            preserve_default=True,
        ),
    ]
