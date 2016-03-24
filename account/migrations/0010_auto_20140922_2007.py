# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import imagekit.models.fields
import account.models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0009_usersettings_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usersettings',
            name='picture',
            field=imagekit.models.fields.ProcessedImageField(upload_to=account.models._user_profile_pic_path),
        ),
    ]
