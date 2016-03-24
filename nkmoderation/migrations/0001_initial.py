# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('account', '0018_auto_20141205_1405'),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContentFlag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField()),
                ('reason', models.CharField(max_length=250)),
                ('status', models.SmallIntegerField(default=1, max_length=1, choices=[(1, 'ilmoitettu'), (2, 'ilmoitus hyl\xe4tty'), (3, 'ilmoitus hyv\xe4ksytty')])),
                ('client_identifier', models.ForeignKey(related_name='flagged_content', to='account.ClientIdentifier')),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('flagger', models.ForeignKey(related_name='flagged_content', to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='contentflag',
            unique_together=set([('flagger', 'content_type', 'object_id'), ('client_identifier', 'content_type', 'object_id')]),
        ),
    ]
