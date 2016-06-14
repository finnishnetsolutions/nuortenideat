# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def copy_original_picture(apps, schema_editor):
    org = apps.get_model('organization', 'Organization')

    for o in org.objects.exclude(picture="").exclude(picture__isnull=True):
        o.original_picture = o.picture.file
        o.save()


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0019_auto_20160527_1134'),
    ]

    operations = [
        migrations.RunPython(copy_original_picture)
    ]
