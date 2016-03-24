# coding=utf-8

from __future__ import unicode_literals

from hashlib import sha256
from uuid import uuid4

from django.conf import settings
from django.contrib.contenttypes.models import ContentType


SETTINGS = getattr(settings, 'ATTACHTOR', {
    'upload_token_salt': settings.SECRET_KEY
})


def get_upload_token(upload_group_id):
    return sha256(';'.join(
        [upload_group_id, SETTINGS['upload_token_salt']]
    )).hexdigest()[:32]


def get_upload_group_id(obj=None):
    if obj is None or obj.pk is None:
        return uuid4().hex

    ct = ContentType.objects.get_for_model(obj)

    return sha256(';'.join(
        [str(obj.pk), str(ct.pk), SETTINGS['upload_token_salt']]
    )).hexdigest()[:32]


def get_upload_signature(obj=None):
    upload_group_id = get_upload_group_id(obj)
    return upload_group_id + get_upload_token(upload_group_id)
