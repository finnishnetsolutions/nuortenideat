# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0031_ideasurvey_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ideasurvey',
            name='content_type',
            field=models.ForeignKey(default=None, to='contenttypes.ContentType'),
        ),
        migrations.AlterField(
            model_name='ideasurvey',
            name='object_id',
            field=models.PositiveIntegerField(default=None),
        ),
        migrations.AlterField(
            model_name='initiative',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_content.initiative_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
    ]
