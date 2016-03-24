# coding=utf-8

from __future__ import unicode_literals

from django import template
from django.contrib.contenttypes.models import ContentType
from tagging.models import Tag
from content.models import Idea
from organization.models import Organization
from favorite.models import Favorite

register = template.Library()


def _get_favorite_model_instance(model_name):
    model_list = [Idea, Tag, Organization]
    for model in model_list:
        if model_name.capitalize() == model.__name__:
            return model
    return None


def _get_favorite_ideas_by_favorite_list(model, id_list):
    if model.__name__ == Tag.__name__:
        return Idea.objects.filter(tags__id__in=id_list)
    elif model.__name__ == Organization.__name__:
        return Idea.objects.filter(target_organizations__id__in=id_list)
    return None


def _get_favorite_objects(ct, user, get_ideas=False):
    model = _get_favorite_model_instance(ct.model)

    obj_ids = Favorite.objects.filter(
        user=user,
        content_type=ct,
    ).values_list('object_id', flat=True)

    if model.__name__ != Idea.__name__ and get_ideas:
        return _get_favorite_ideas_by_favorite_list(model, obj_ids)

    return model.objects.filter(pk__in=obj_ids)


@register.inclusion_tag('favorite/follow_idea_link.html', takes_context=True)
def fav_link(context, obj=None):
    return {
        'obj': obj,
        'ct': ContentType.objects.get_for_model(obj),
        'perm': context['perm']
    }

@register.assignment_tag()
def fav_list(ct_id, user, get_ideas=False):
    ct = ContentType.objects.get(pk=ct_id)
    return _get_favorite_objects(ct, user, get_ideas).distinct()

@register.assignment_tag()
def fav_get_ct_id(natural_key):
    return ContentType.objects.get_by_natural_key(*natural_key.split('.')).pk