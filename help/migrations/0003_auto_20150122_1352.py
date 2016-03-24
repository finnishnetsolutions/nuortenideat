# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import libs.multilingo.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('help', '0002_auto_20141229_1634'),
    ]

    operations = [
        migrations.AddField(
            model_name='instruction',
            name='connect_link_type',
            field=models.CharField(null=True, default=None, choices=[(None, 'ei mit\xe4\xe4n'), ('privacy-policy', 'rekisteriseloste'), ('contact-details', 'yhteystiedot')], max_length=50, blank=True, unique=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='instruction',
            name='description',
            field=libs.multilingo.models.fields.MultilingualTextField(default='', help_text=None, verbose_name='Sis\xe4lt\xf6'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='instruction',
            name='title',
            field=libs.multilingo.models.fields.MultilingualTextField(default='', help_text=None, max_length=255, verbose_name='Otsikko'),
            preserve_default=True,
        ),
    ]
