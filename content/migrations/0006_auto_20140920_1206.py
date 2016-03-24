# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import redactor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0005_auto_20140919_1950'),
    ]

    operations = [
        migrations.AlterField(
            model_name='initiative',
            name='description',
            field=redactor.fields.RedactorField(verbose_name='kuvaus'),
        ),
    ]
