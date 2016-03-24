 # -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.translation import ugettext_lazy as _


def create_default_organizations(apps, schema_editor):
    Organization = apps.get_model('organization', 'Organization')

    # Model history doesnt contain class constants, let's set what we need.
    Organization.TYPE_NATION = 1
    Organization.TYPE_UNKNOWN = 0

    Organization.objects.get_or_create(type=Organization.TYPE_NATION,
                                       name=_("Valtakunta"))
    Organization.objects.get_or_create(type=Organization.TYPE_UNKNOWN,
                                       name=_("Tuntematon"))

class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0002_auto_20140915_1516'),
    ]

    operations = [
        migrations.RunPython(create_default_organizations)
    ]
