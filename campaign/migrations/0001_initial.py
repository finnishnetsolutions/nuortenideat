# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import nuka.models
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Campaign',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', nuka.models.MultilingualTextField(default='', help_text=None, max_length=255, verbose_name='Otsikko')),
                ('description', nuka.models.MultilingualTextField(default='', help_text=None, verbose_name='Sis\xe4lt\xf6')),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
                ('parent', mptt.fields.TreeForeignKey(related_name='children', blank=True, to='campaign.Campaign', null=True)),
            ],
            options={
                'verbose_name': 'Kampanja',
                'verbose_name_plural': 'Kampanjat',
            },
            bases=(models.Model,),
        ),
    ]
