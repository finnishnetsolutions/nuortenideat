# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models, migrations


def add_tags(apps, schema_editor):
    tags = [
        "Asuminen",
        "Rakentaminen",
        "Luonto",
        "Ympäristö",
        "Koulu",
        "Opiskelu",
        "Kulttuuri",
        "Työelämä",
        "Vapaa-aika",
        "Harrastukset",
        "Tapahtumat",
        "Matkailu",
        "Liikenne",
        "Palvelut",
        "Terveys",
        "Muut"
    ]

    # Remove tags from ideas.
    Idea = apps.get_model("content", "Idea")
    for idea in Idea.objects.all():
        idea.tags.clear()

    # Delete all tags and add the new ones.
    Tag = apps.get_model("tagging", "Tag")
    Tag.objects.all().delete()
    for tag in tags:
        Tag.objects.create(name=tag)


class Migration(migrations.Migration):

    dependencies = [
        ('tagging', '0002_auto_20140915_1827'),
        ('content', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_tags)
    ]
