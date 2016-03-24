# coding=utf-8

from __future__ import unicode_literals

from django import template
from django.contrib.contenttypes.models import ContentType

from nkmoderation.models import ModerationReason


register = template.Library()


@register.simple_tag
def moderated_object_url(moderated_object):
    return moderated_object.moderator.get_object_url(
        obj=moderated_object.content_object
    )


@register.inclusion_tag('nkmoderation/object_moderation_reasons.html')
def moderation_reasons(obj):
    if not hasattr(obj, '_moderation_reasons_cache'):
        ct = ContentType.objects.get_for_model(obj)
        reasons = list(ModerationReason.objects.filter(
            content_type=ct, object_id=obj.pk
        ).order_by('-pk'))
        setattr(obj, '_moderation_reasons_cache', reasons)
    return {'reasons': reasons, }
