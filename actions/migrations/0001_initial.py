# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Action',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=16, choices=[('created', 'created'), ('updated', 'updated'), ('deleted', 'deleted')])),
                ('subtype', models.CharField(max_length=30)),
                ('object_id', models.PositiveIntegerField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('actor', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
