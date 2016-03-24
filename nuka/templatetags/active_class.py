# coding=utf-8

from __future__ import unicode_literals

from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def class_active_if_url(context, *url_names):
    if 'request' in context:
        rmatch = context['request'].resolver_match
        if rmatch is not None:
            for name in url_names:
                if name in (rmatch.url_name, rmatch.view_name):
                    return ' class="active"'
    return ''


@register.simple_tag(takes_context=True)
def class_active_if_namespace(context, *namespaces):
    if 'request' in context:
        rmatch = context['request'].resolver_match
        if rmatch is not None:
            for ns in namespaces:
                if ns in rmatch.namespaces:
                    return ' class="active"'
    return ''
