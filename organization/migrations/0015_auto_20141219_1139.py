# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def activate_existing_organization(apps, schema_editor):
    """Activate organizations created before activation moderation/activation was
    possible."""

    Organization = apps.get_model("organization", "Organization")
    Organization.objects.all().update(is_active=True)


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0014_auto_20141219_1139'),
    ]

    operations = [
        migrations.RunPython(activate_existing_organization)
    ]
