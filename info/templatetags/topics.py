# coding=utf-8

from __future__ import unicode_literals

from django import template
from info.models import Topic

register = template.Library()


def _get_latest_topics():
    return Topic.objects.all().order_by('-date')[:3]


@register.inclusion_tag('info/topics.html')
def latest_topics():
    return {'topics': _get_latest_topics()}