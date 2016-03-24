# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('subject', models.CharField(max_length=255, verbose_name='aihe')),
                ('message', models.CharField(max_length=4000, verbose_name='viesti')),
                ('warning', models.BooleanField(default=False)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('read_receivers', models.ManyToManyField(related_name='read_messages', to=settings.AUTH_USER_MODEL)),
                ('receivers', models.ManyToManyField(related_name='messages', to=settings.AUTH_USER_MODEL)),
                ('reply_to', models.ForeignKey(related_name='replies', on_delete=django.db.models.deletion.SET_NULL, to='nkmessages.Message', null=True)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
