# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0006_auto_20140920_1206'),
    ]

    operations = [
        migrations.AlterField(
            model_name='initiative',
            name='target_organizations',
            field=models.ManyToManyField(related_name='targeted_initiatives', verbose_name='kohde organisaatiot', to=b'organization.Organization'),
        ),
    ]
