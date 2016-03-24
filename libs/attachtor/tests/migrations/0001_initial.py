# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from ...models import fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Blog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=100)),
                ('content',fields.RedactorAttachtorField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
