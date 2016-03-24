# coding=utf-8

from __future__ import unicode_literals

from django import template

from ..models import Organization


register = template.Library()


@register.filter
def type_name(type_id):
    """ Returns the type's name by it's given id. """
    return next((v for k, v in Organization.TYPE_CHOICES if k == type_id), None)