# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
        ('nkmessages', '0003_auto_20141212_1528'),
    ]

    operations = [
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('message_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='nkmessages.Message')),
                ('name', models.CharField(max_length=50, verbose_name='nimi', blank=True)),
                ('email', models.EmailField(max_length=75, verbose_name='s\xe4hk\xf6posti', blank=True)),
            ],
            options={
                'verbose_name': 'Palaute',
                'verbose_name_plural': 'Palautteet',
            },
            bases=('nkmessages.message',),
        ),
        migrations.AddField(
            model_name='message',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_nkmessages.message_set', editable=False, to='contenttypes.ContentType', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='message',
            name='to_moderator',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
