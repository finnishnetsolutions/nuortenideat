# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from content.models import Idea


def set_timestamp(apps, schema_editor):
    idea_model = apps.get_model('content', 'Idea')
    ideas = idea_model.objects.filter(status=Idea.STATUS_DECISION_GIVEN, decision_given=None)
    for idea in ideas:
        idea.decision_given = idea.modified
        idea.save()


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0019_archived_timestamp'),
    ]

    operations = [
        migrations.RunPython(set_timestamp),
    ]
