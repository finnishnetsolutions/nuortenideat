# coding=utf-8

from __future__ import unicode_literals

from django import template

import json
from django.template.defaultfilters import safe

register = template.Library()


@register.filter()
def jsonize(obj):
    return safe(json.dumps(obj))
