# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0027_auto_20160527_1131'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', verbose_name='groups'),
        ),
        migrations.AlterField(
            model_name='user',
            name='joined',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='liittynyt'),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_login',
            field=models.DateTimeField(null=True, verbose_name='last login', blank=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='status',
            field=models.SmallIntegerField(default=0, verbose_name='tila', choices=[(0, 'Odottaa aktivointia'), (1, 'Aktiivinen'), (5, 'Arkistoitu')]),
        ),
    ]
