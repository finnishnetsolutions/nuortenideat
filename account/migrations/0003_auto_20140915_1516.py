# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_auto_20140903_1618'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='status',
            field=models.SmallIntegerField(default=0, max_length=10, verbose_name='tila', choices=[(0, 'Odottaa aktivointia'), (1, 'Aktiivinen'), (5, 'Arkistoitu')]),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(help_text='Enint\xe4\xe4n 30 merkki\xe4. Vain kirjaimet, numerot ja _ ovat sallittuja.', unique=True, max_length=30, verbose_name='k\xe4ytt\xe4j\xe4nimi', validators=[django.core.validators.RegexValidator('^[\\w]+$', 'Enter a valid username.', 'invalid')]),
        ),
    ]
