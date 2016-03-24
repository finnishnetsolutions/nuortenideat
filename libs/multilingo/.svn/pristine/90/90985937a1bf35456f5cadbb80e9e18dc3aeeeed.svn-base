# coding=utf-8

from __future__ import unicode_literals

from django.conf import settings


CONF = {
    'languages': settings.LANGUAGES,
    'default_language': settings.LANGUAGE_CODE,
    'remove_empty_translations': True
}

CONF.update(
    getattr(settings, 'MULTILINGO', {})
)
