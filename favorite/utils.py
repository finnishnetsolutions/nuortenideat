# coding=utf-8

from __future__ import unicode_literals
from django.contrib.contenttypes.models import ContentType
from tagging.models import Tag
from content.models import Idea, Initiative
from organization.models import Organization
from favorite.models import Favorite


def _get_favorite_model_instance(model_name):
    model_list = [Idea, Tag, Organization]
    for model in model_list:
        if model_name.capitalize() == model.__name__:
            return model
    return None


def _get_favorite_initiatives_by_favorite_list(model, id_list):
    if model.__name__ == Tag.__name__:
        return Initiative.objects.filter(tags__id__in=id_list)
    elif model.__name__ == Organization.__name__:
        return Initiative.objects.filter(target_organizations__id__in=id_list)
    return None


def get_ct_id_by_natural_key(natural_key):
    return ContentType.objects.get_by_natural_key(*natural_key.split('.')).pk


def get_favorite_objects(ct_id, user, get_ideas=False):
    ct = ContentType.objects.get(pk=ct_id)
    model = _get_favorite_model_instance(ct.model)
    obj_ids = Favorite.objects.filter(
        user=user,
        content_type=ct,
    ).values_list('object_id', flat=True)

    if model.__name__ != Idea.__name__ and get_ideas:
        return _get_favorite_initiatives_by_favorite_list(model, obj_ids)

    return model.objects.filter(pk__in=obj_ids)


def get_favorite_objects_by_natural_key(nk, user, get_ideas=False):
    ct_id = get_ct_id_by_natural_key(nk)
    return get_favorite_objects(ct_id, user, get_ideas)
