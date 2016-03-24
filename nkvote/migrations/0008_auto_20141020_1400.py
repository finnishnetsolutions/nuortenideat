# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0014_merge'),
        ('nkvote', '0007_auto_20141020_1031'),
    ]

    operations = [
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('choices', models.ManyToManyField(to='nkvote.Option')),
                ('client_identifier', models.ForeignKey(to='account.ClientIdentifier')),
                ('gallup', models.ForeignKey(to='nkvote.Gallup')),
                ('voter', models.ForeignKey(to='nkvote.Voter')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='choice',
            name='client_identifier',
        ),
        migrations.RemoveField(
            model_name='choice',
            name='option',
        ),
        migrations.RemoveField(
            model_name='choice',
            name='voter',
        ),
        migrations.DeleteModel(
            name='Choice',
        ),
        migrations.AlterField(
            model_name='option',
            name='text',
            field=models.CharField(max_length=100, verbose_name='vaihtoehto'),
        ),
        migrations.AlterField(
            model_name='question',
            name='text',
            field=models.CharField(max_length=150, verbose_name='kysymys'),
        ),
    ]
