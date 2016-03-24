# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('organization', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='admin',
            options={'verbose_name': 'Yhteyshenkil\xf6t'},
        ),
        migrations.AlterModelOptions(
            name='organization',
            options={'verbose_name': 'Organisaatio', 'verbose_name_plural': 'Organisaatiot'},
        ),
        migrations.AddField(
            model_name='organization',
            name='admins',
            field=models.ManyToManyField(related_name='organizations', through='organization.Admin', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
