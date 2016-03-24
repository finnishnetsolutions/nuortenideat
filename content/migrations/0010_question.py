# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0009_auto_20141013_1507'),
    ]

    operations = [
        migrations.CreateModel(
            name='Question',
            fields=[
                ('initiative_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='content.Initiative')),
                ('user_name', models.CharField(max_length=100)),
            ],
            options={
                'abstract': False,
            },
            bases=('content.initiative',),
        ),
    ]
