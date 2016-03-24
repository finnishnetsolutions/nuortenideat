# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
        ('actions', '0002_auto_20150612_1531'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('send_instantly', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('action', models.ForeignKey(related_name='notifications', to='actions.Action')),
                ('recipient', models.ForeignKey(related_name='notifications', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('-id',),
                'get_latest_by': 'action__created',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SentEmails',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField()),
                ('email', models.CharField(max_length=254)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='notification',
            unique_together=set([('action', 'recipient')]),
        ),
    ]
