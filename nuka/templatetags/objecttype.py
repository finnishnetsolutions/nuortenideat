# coding=utf-8

from __future__ import unicode_literals

from django import template

register = template.Library()


@register.filter
def verbose_name(obj, plural=False):
    return obj._meta.verbose_name_plural if plural else obj._meta.verbose_name
