# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='status',
            field=models.SmallIntegerField(max_length=10, verbose_name='tila', choices=[(0, 'Odottaa aktivointia'), (1, 'Aktiivinen'), (5, 'Arkistoitu')]),
        ),
        migrations.AlterField(
            model_name='usersettings',
            name='first_name',
            field=models.CharField(max_length=50, verbose_name='etunimi'),
        ),
        migrations.AlterField(
            model_name='usersettings',
            name='language',
            field=models.CharField(default='fi', max_length=5, verbose_name='kieli', choices=[('fi', 'suomi'), ('sv', 'ruotsi')]),
        ),
        migrations.AlterField(
            model_name='usersettings',
            name='last_name',
            field=models.CharField(max_length=50, verbose_name='sukunimi'),
        ),
        migrations.AlterField(
            model_name='usersettings',
            name='phone_number',
            field=models.CharField(default=None, max_length=25, null=True, verbose_name='puhelinnumero', blank=True),
        ),
    ]
