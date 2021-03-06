# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('favorite', '0002_auto_20141216_1558'),
    ]

    operations = [
        migrations.AlterField(
            model_name='favorite',
            name='user',
            field=models.ForeignKey(related_name='favorites', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
