# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
        ('content', '0027_auto_20160609_1207'),
    ]

    operations = [
        migrations.CreateModel(
            name='IdeaSurvey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField(null=True)),
                ('status', models.SmallIntegerField(default=1)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('opened', models.DateTimeField(null=True)),
                ('closed', models.DateTimeField(null=True)),
                ('interaction', models.SmallIntegerField(default=1, verbose_name='Kuka saa vastata gallupiin?', choices=[(1, 'Kaikki'), (2, 'Rekister\xf6ityneet k\xe4ytt\xe4j\xe4t')])),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType', null=True)),
                ('idea', models.ForeignKey(related_name='idea_surveys', to='content.Idea')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
