# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('nkvote', '0012_gallup_interaction'),
    ]

    operations = [
        migrations.AlterField(
            model_name='voter',
            name='user',
            field=models.ForeignKey(default=None, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
