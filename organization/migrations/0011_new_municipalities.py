# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def new_municipalities(apps, schema_editor):
    Organization = apps.get_model("organization", "Organization")
    Municipality = apps.get_model("fimunicipality", "Municipality")

    for org in Organization.objects.all():
        if org.municipality is not None:
            mun = Municipality.objects.filter(
                name_fi__contains=org.municipality.name
            ).first()
            if mun:
                org.municipalities.add(mun)


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0010_organization_municipalities'),
    ]

    operations = [
        migrations.RunPython(new_municipalities)
    ]
