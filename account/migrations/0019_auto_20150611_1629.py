# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
        ('account', '0018_auto_20141205_1405'),
    ]

    operations = [
        migrations.CreateModel(
            name='NotificationOptions',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('role', models.CharField(max_length=50)),
                ('action_type', models.CharField(max_length=100)),
                ('action_subtype', models.CharField(max_length=100)),
                ('cancelled', models.BooleanField(default=False)),
                ('notify_at_once', models.BooleanField(default=False)),
                ('notify_daily', models.BooleanField(default=False)),
                ('notify_weekly', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('user', models.ForeignKey(related_name='user_notifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='notificationoptions',
            unique_together=set([('user', 'content_type', 'role', 'action_type', 'action_subtype')]),
        ),
    ]
