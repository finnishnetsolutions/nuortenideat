# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from content.models import Initiative


def set_archived_timestamp(apps, schema_editor):
    Idea = apps.get_model('content', 'Idea')
    for idea in Idea.objects.filter(visibility=Initiative.VISIBILITY_ARCHIVED):
        idea.archived = idea.modified
        idea.save()


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0018_initiative_archived'),
    ]

    operations = [
        migrations.RunPython(set_archived_timestamp),
    ]
