# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0011_new_municipalities'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='organization',
            name='municipality',
        ),
        migrations.AlterField(
            model_name='organization',
            name='municipalities',
            field=models.ManyToManyField(related_name='Kunnat', verbose_name='Valitse kunnat, joiden alueella organisaatio toimii.', to=b'fimunicipality.Municipality'),
        ),
    ]
