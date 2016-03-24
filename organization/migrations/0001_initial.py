# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Admin',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_active', models.BooleanField(default=False, verbose_name='aktiivinen')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Municipality',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.SmallIntegerField(verbose_name='tyyppi', choices=[(1, 'Koko Suomi'), (3, 'J\xe4rjest\xf6'), (4, 'Kunta'), (5, 'Koulu tai muu oppilaitos'), (10, 'Muu organisaatio')])),
                ('name', models.CharField(max_length=255, verbose_name='nimi')),
                ('is_active', models.BooleanField(default=False, verbose_name='aktiivinen')),
                ('created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='luotu')),
                ('municipality', models.ForeignKey(default=None, to='organization.Municipality', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='admin',
            name='organization',
            field=models.ForeignKey(to='organization.Organization'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='admin',
            name='user',
            field=models.ForeignKey(related_name='admins', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
