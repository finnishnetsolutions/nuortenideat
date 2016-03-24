# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
        ('nkmoderation', '0002_auto_20141216_0025'),
    ]

    operations = [
        migrations.CreateModel(
            name='ModerationReason',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField()),
                ('timestamp', models.DateTimeField(default=datetime.datetime(2015, 1, 16, 12, 50, 18, 33570))),
                ('reason', models.CharField(max_length=250)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('moderator', models.ForeignKey(related_name='moderated_content', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterIndexTogether(
            name='moderationreason',
            index_together=set([('content_type', 'object_id')]),
        ),
    ]
