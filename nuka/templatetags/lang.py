# coding=utf-8

from __future__ import unicode_literals

from operator import itemgetter
import re

from django import template
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.translation import override


register = template.Library()

lang_prefix = re.compile(r'^\/(%s)\/' % '|'.join(map(itemgetter(0), settings.LANGUAGES)))


@register.simple_tag(takes_context=True)
def lang_switch(context, lang=None):
    request = context['request']
    return lang_prefix.sub('/%s/' % lang, request.get_full_path())


@register.simple_tag(takes_context=True)
def include_translated(context, template_name, lang):
    with override(lang):
        html = render_to_string(template_name, context)
    return html