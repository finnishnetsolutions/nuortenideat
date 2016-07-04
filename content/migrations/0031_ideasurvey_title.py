# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import nuka.models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0030_auto_20160621_1530'),
    ]

    operations = [
        migrations.AddField(
            model_name='ideasurvey',
            name='title',
            field=nuka.models.MultilingualTextField(default='', help_text=None, max_length=255, verbose_name='otsikko'),
            preserve_default=True,
        ),
    ]
