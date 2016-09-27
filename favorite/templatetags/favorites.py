# coding=utf-8

from __future__ import unicode_literals

from django import template
from django.contrib.contenttypes.models import ContentType
from favorite.utils import get_favorite_objects, get_ct_id_by_natural_key

register = template.Library()


@register.inclusion_tag('favorite/follow_idea_link.html', takes_context=True)
def fav_link(context, obj=None):
    return {
        'obj': obj,
        'ct': ContentType.objects.get_for_model(obj),
        'perm': context['perm']
    }


@register.assignment_tag()
def fav_list(ct_id, user, get_ideas=False):
    return get_favorite_objects(ct_id, user, get_ideas).distinct()


@register.assignment_tag()
def fav_get_ct_id(natural_key):
    return get_ct_id_by_natural_key(natural_key)
