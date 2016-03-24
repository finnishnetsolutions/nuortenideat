# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('kuaapi', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='kuainitiative',
            name='created_by',
            field=models.ForeignKey(default=None, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='kuainitiative',
            name='edit_link',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
    ]
