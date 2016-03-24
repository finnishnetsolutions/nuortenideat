# coding=utf-8

from __future__ import unicode_literals

from django import template
from django.conf import settings
from django.utils.translation import ugettext_noop

register = template.Library()


ugettext_noop("https://www.nuortenideat.fi/")


@register.assignment_tag()
def base_url():
    return settings.BASE_URL

@register.assignment_tag()
def practice_environment():
    return settings.PRACTICE
