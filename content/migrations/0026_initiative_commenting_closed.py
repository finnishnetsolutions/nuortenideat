# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0025_question_user_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='initiative',
            name='commenting_closed',
            field=models.BooleanField(default=False, verbose_name='kommentointi suljettu'),
            preserve_default=True,
        ),
    ]
