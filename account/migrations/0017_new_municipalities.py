# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def new_municipalities(apps, schema_editor):
    UserSettings = apps.get_model("account", "UserSettings")
    Municipality = apps.get_model("fimunicipality", "Municipality")

    for us in UserSettings.objects.all():
        if us.old_municipality is not None:
            us.municipality = Municipality.objects.filter(
                name_fi__contains=us.old_municipality.name
            ).first()
        if us.municipality is None:
            us.municipality = Municipality.objects.get(
                code='049'
            )
        us.save()


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0016_usersettings_municipality'),
    ]

    operations = [
        migrations.RunPython(new_municipalities)
    ]
