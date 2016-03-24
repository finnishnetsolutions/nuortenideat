# coding=utf-8

from __future__ import unicode_literals

from django import template
from django.conf import settings
from django.core.urlresolvers import reverse


register = template.Library()


@register.assignment_tag
def openapi_version():
    return settings.OPEN_API['version']

@register.assignment_tag
def openapi_url():
    return reverse('openapi:api-root')

@register.assignment_tag
def openapi_docs_url():
    return reverse('openapi:django.swagger.base.view')