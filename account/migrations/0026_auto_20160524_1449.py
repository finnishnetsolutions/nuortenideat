# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def copy_original_picture(apps, schema_editor):
    user_settings = apps.get_model('account', 'UserSettings')

    for s in user_settings.objects.exclude(picture="").exclude(picture__isnull=True):
        s.original_picture = s.picture.file
        s.save()


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0025_usersettings_original_picture'),
    ]

    operations = [
        migrations.RunPython(copy_original_picture)
    ]
