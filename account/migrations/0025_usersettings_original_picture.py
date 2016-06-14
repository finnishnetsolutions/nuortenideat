# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import imagekit.models.fields
import account.models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0024_usersettings_cropping'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersettings',
            name='original_picture',
            field=imagekit.models.fields.ProcessedImageField(default="", upload_to=account.models._user_profile_pic_path),
            preserve_default=True,
        ),
    ]
