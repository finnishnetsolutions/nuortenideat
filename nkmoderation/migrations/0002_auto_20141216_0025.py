# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('nkmoderation', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='contentflag',
            name='created',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='contentflag',
            name='updated',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='contentflag',
            name='flagger',
            field=models.ForeignKey(related_name='flagged_content', verbose_name='ilmoittaja', to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='contentflag',
            name='reason',
            field=models.CharField(help_text='Kerro lyhyesti, mik\xe4 tekee sis\xe4ll\xf6st\xe4 asiattoman. Enint\xe4\xe4n 250 merkki\xe4.', max_length=250, verbose_name='syy ilmoitukseen'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='contentflag',
            name='status',
            field=models.SmallIntegerField(default=1, max_length=1, verbose_name='tila', choices=[(1, 'ilmoitettu'), (2, 'ilmoitus hyl\xe4tty'), (3, 'ilmoitus hyv\xe4ksytty')]),
            preserve_default=True,
        ),
    ]
