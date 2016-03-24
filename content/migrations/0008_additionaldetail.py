# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0007_auto_20141007_1651'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdditionalDetail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('detail', models.TextField(verbose_name='lis\xe4tieto')),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('idea', models.ForeignKey(to='content.Idea')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
