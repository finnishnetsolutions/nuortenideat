# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import image_cropping.fields
import imagekit.models.fields
import cropping.fields
import account.models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0026_auto_20160524_1449'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usersettings',
            name=b'cropping',
            field=image_cropping.fields.ImageRatioField('original_picture', '220x220', hide_image_field=False, size_warning=True, allow_fullsize=False, free_crop=False, adapt_rotation=False, help_text=None, verbose_name='Profiilikuvan rajaus'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='usersettings',
            name='original_picture',
            field=cropping.fields.ProcessedImageFieldWithCropping(default='', upload_to=account.models._user_profile_pic_path),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='usersettings',
            name='picture',
            field=imagekit.models.fields.ProcessedImageField(max_length=120, upload_to=account.models._user_profile_pic_path),
            preserve_default=True,
        ),
    ]
