# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import imagekit.models.fields
import organization.models


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0007_organization_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='picture',
            field=imagekit.models.fields.ProcessedImageField(default=None, null=True, upload_to=organization.models._organization_pic_path, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='organization',
            name='description',
            field=models.TextField(default='', verbose_name='kuvaus', blank=True),
        ),
        migrations.AlterField(
            model_name='organization',
            name='municipality',
            field=models.ForeignKey(default=None, to='organization.Municipality', blank=True, help_text='Valitse kunta, jos organisaatio on kunta tai jos organisaation toiminta keskittyy tietyn kunnan aluellee.', null=True, verbose_name='Kunta'),
        ),
    ]
