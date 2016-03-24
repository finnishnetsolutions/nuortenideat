# coding: utf-8

from __future__ import unicode_literals

from operator import attrgetter

from tagging.models import Tag


def tags_by_popularity():
    return sorted(Tag.objects.all(), key=attrgetter("popularity"), reverse=True)
