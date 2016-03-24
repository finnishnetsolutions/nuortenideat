# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comments', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomComment',
            fields=[
            ],
            options={
                'ordering': ('submit_date',),
                'proxy': True,
            },
            bases=('comments.comment',),
        ),
    ]
