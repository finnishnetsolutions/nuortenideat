# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def rename_nation_organization(apps, schema_editor):
    Organization = apps.get_model('organization', 'Organization')

    # Model history doesnt contain class constants, let's set what we need.
    Organization.TYPE_NATION = 1

    nation_org = Organization.objects.get(type=Organization.TYPE_NATION)
    nation_org.name = "Koko Suomi"
    nation_org.save();


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0008_auto_20141007_1651'),
    ]

    operations = [
        migrations.RunPython(rename_nation_organization)
    ]
