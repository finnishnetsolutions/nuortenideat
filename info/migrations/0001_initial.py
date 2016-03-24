# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, verbose_name='Otsikko')),
                ('description', models.TextField(verbose_name='Sis\xe4lt\xf6')),
                ('date', models.DateTimeField(default=None, null=True, blank=True)),
            ],
            options={
                'verbose_name': 'Ajankohtaista',
                'verbose_name_plural': 'Ajankohtaiset',
            },
            bases=(models.Model,),
        ),
    ]
