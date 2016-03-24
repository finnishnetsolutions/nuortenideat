# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0003_default_organizations'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='municipality',
            options={'verbose_name': 'Kunta', 'verbose_name_plural': 'Kunnat'},
        ),
        migrations.AlterField(
            model_name='organization',
            name='municipality',
            field=models.ForeignKey(default=None, blank=True, to='organization.Municipality', null=True),
        ),
        migrations.AlterField(
            model_name='organization',
            name='type',
            field=models.SmallIntegerField(verbose_name='tyyppi', choices=[(0, 'Tuntematon'), (1, 'Koko Suomi'), (3, 'J\xe4rjest\xf6'), (4, 'Kunta'), (5, 'Koulu tai muu oppilaitos'), (10, 'Muu organisaatio')]),
        ),
    ]
