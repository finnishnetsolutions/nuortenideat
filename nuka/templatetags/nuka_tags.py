# coding=utf-8

from __future__ import unicode_literals
from bootstrap3.templatetags.bootstrap3 import get_pagination_context

from django import template
from django.conf import settings
from django.template.base import render_value_in_context, TemplateSyntaxError, Node
from survey.conf import config as survey_config

register = template.Library()


@register.inclusion_tag('bootstrap3/ajaxy_pagination.html')
def bootstrap_ajaxy_pagination(page, **kwargs):
    pagination_kwargs = kwargs.copy()
    pagination_kwargs['page'] = page
    return get_pagination_context(**pagination_kwargs)


@register.assignment_tag()
def get_survey_result_choices():
    return survey_config.show_results_choices


@register.filter(is_safe=False)
def og_pic_url(obj=None):
    pic_url = '{}{}'.format(settings.STATIC_URL, settings.FB_LOGO_URL)
    if obj is not None and hasattr(obj, 'picture') and obj.picture:
        if hasattr(obj, 'picture_main'):
            return obj.picture_main.url
        elif hasattr(obj, 'picture_medium'):
            return obj.picture_medium.url
    return pic_url
