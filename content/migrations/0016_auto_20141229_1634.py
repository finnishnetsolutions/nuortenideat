# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import libs.attachtor.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0015_initiative_premoderation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='additionaldetail',
            name='detail',
            field=libs.attachtor.models.fields.RedactorAttachtorField(verbose_name='lis\xe4tieto'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='initiative',
            name='description',
            field=libs.attachtor.models.fields.RedactorAttachtorField(verbose_name='kuvaus'),
            preserve_default=True,
        ),
    ]
