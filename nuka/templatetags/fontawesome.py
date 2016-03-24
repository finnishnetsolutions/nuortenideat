# coding=utf-8

from __future__ import unicode_literals

from django import template
from django.utils.html import escape

register = template.Library()


@register.simple_tag
def fa_icon(name, size=None, alt=None):
    size_class = '' if size is None else ' fa-%s' % str(size)
    alt_html = '' if alt is None else '<span class="sr-only">%s</span>' % escape(alt)
    return '<i class="fa fa-%s%s">%s</i>' % (name, size_class, alt_html)
