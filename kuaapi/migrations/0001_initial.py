# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0010_question'),
        ('fimunicipality', '0003_auto_20141020_1401'),
    ]

    operations = [
        migrations.CreateModel(
            name='KuaInitiative',
            fields=[
                ('kua_id', models.IntegerField(serialize=False, primary_key=True)),
                ('initiative', models.OneToOneField(related_name=b'kua_initiative', to='content.Initiative')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='KuaInitiativeStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(max_length=15, choices=[(b'draft', 'Luonnos'), (b'published', 'Julkaistu')])),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('kua_initiative', models.ForeignKey(related_name=b'statuses', to='kuaapi.KuaInitiative')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ParticipatingMunicipality',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('municipality', models.OneToOneField(related_name=b'kua_participation', to='fimunicipality.Municipality')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
