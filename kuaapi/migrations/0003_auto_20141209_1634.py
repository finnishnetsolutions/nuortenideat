# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0013_auto_20141209_1634'),
        ('kuaapi', '0002_auto_20141208_1739'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='kuainitiativestatus',
            options={'ordering': ('-pk',), 'verbose_name_plural': 'Kua statuses'},
        ),
        migrations.RemoveField(
            model_name='kuainitiative',
            name='initiative',
        ),
        migrations.AddField(
            model_name='kuainitiative',
            name='idea',
            field=models.OneToOneField(related_name='kua_initiative', default=None, to='content.Idea'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='kuainitiativestatus',
            name='status',
            field=models.CharField(max_length=15, choices=[('draft', 'Luonnos'), ('published', 'Julkaistu'), ('decision-given', 'P\xe4\xe4t\xf6s annettu')]),
        ),
    ]
