# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='surveyelement',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_survey.surveyelement_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
    ]
