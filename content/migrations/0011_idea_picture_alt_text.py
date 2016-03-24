# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0010_question'),
    ]

    operations = [
        migrations.AddField(
            model_name='idea',
            name='picture_alt_text',
            field=models.CharField(default=None, max_length=255, verbose_name='kuvan tekstimuotoinen kuvaus'),
            preserve_default=True,
        ),
    ]
