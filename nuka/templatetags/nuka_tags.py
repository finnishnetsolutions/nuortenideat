# coding=utf-8

from __future__ import unicode_literals
from bootstrap3.templatetags.bootstrap3 import get_pagination_context

from django import template
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


