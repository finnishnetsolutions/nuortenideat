# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0014_merge'),
        ('content', '0009_auto_20141013_1507'),
        ('nkvote', '0006_auto_20141009_1105'),
    ]

    operations = [
        migrations.CreateModel(
            name='Choice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('client_identifier', models.ForeignKey(to='account.ClientIdentifier')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Gallup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.SmallIntegerField(default=1)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('closed', models.DateTimeField(null=True)),
                ('idea', models.ForeignKey(to='content.Idea')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Option',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.CharField(max_length=100, verbose_name='vaihtoehtoteksti')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.CharField(max_length=150, verbose_name='kysymysteksti')),
                ('gallup', models.ForeignKey(to='nkvote.Gallup')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='option',
            name='question',
            field=models.ForeignKey(to='nkvote.Question'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='choice',
            name='option',
            field=models.ForeignKey(to='nkvote.Option'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='choice',
            name='voter',
            field=models.ForeignKey(to='nkvote.Voter'),
            preserve_default=True,
        ),
    ]
