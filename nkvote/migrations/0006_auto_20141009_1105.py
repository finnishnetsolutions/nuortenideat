# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0013_auto_20141002_1453'),
        ('contenttypes', '0001_initial'),
        ('nkvote', '0005_auto_20141009_1104'),
    ]

    operations = [
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('choice', models.SmallIntegerField()),
                ('client_identifier', models.ForeignKey(to='account.ClientIdentifier')),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('voter', models.ForeignKey(to='nkvote.Voter')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='vote',
            unique_together=set([('voter', 'content_type', 'object_id')]),
        ),
    ]
