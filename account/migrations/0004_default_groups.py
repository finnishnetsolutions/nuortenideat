# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.models import Group

from django.db import models, migrations


def create_default_groups(apps, schema_editor):
    from .. import models
    Group.objects.get_or_create(name=models.GROUP_NAME_MODERATORS)
    Group.objects.get_or_create(name=models.GROUP_NAME_ADMINS)


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_auto_20140915_1516'),
    ]

    operations = [
        migrations.RunPython(create_default_groups)
    ]
