# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nkvote', '0009_auto_20141021_1335'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='option',
            options={'ordering': ['question', 'seq_number']},
        ),
        migrations.AlterModelOptions(
            name='question',
            options={'ordering': ['gallup', 'seq_number']},
        ),
        migrations.AddField(
            model_name='gallup',
            name='default_view',
            field=models.SmallIntegerField(default=1),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='answer',
            unique_together=set([('voter', 'gallup')]),
        ),
    ]
