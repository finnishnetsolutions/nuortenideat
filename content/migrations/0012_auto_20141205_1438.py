# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0011_idea_picture_alt_text'),
    ]

    operations = [
        migrations.AlterField(
            model_name='idea',
            name='picture_alt_text',
            field=models.CharField(default=None, max_length=255, null=True, verbose_name='kuvan tekstimuotoinen kuvaus'),
        ),
    ]
