# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0008_additionaldetail'),
    ]

    operations = [
        migrations.AlterField(
            model_name='additionaldetail',
            name='idea',
            field=models.ForeignKey(related_name='details', to='content.Idea'),
        ),
    ]
