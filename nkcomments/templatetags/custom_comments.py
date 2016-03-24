# coding=utf-8

from __future__ import unicode_literals

from django import template

from ..utils import get_form


register = template.Library()


@register.simple_tag(takes_context=True)
def get_custom_comment_form(context, obj, varname='form'):
    context[varname] = get_form(context['request'], obj)
    return ''


@register.filter
def get_comment_vote(comment, comment_votes):
    for comment_vote in comment_votes:
        if comment_vote.object_id == comment.pk:
            return comment_vote
    return None
