# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import cropping.fields
import imagekit.models.fields
import image_cropping.fields
import organization.models


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0018_organization_cropping'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='original_picture',
            field=cropping.fields.ProcessedImageFieldWithCropping(default='', upload_to=organization.models._organization_pic_path),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='organization',
            name=b'cropping',
            field=image_cropping.fields.ImageRatioField('original_picture', '220x220', hide_image_field=False, size_warning=True, allow_fullsize=False, free_crop=False, adapt_rotation=False, help_text=None, verbose_name='Profiilikuvan rajaus'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='organization',
            name='picture',
            field=imagekit.models.fields.ProcessedImageField(default=None, max_length=120, null=True, upload_to=organization.models._organization_pic_path, blank=True),
            preserve_default=True,
        ),
    ]
