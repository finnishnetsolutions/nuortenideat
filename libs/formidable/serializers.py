# coding=utf-8

from __future__ import unicode_literals

from django.utils.encoding import force_text
from django.utils.functional import Promise

from simplejson.encoder import JSONEncoderForHTML


class LazyJSONEncoderMixIn(object):
    """Encodes django's lazy i18n strings. Used to serialize translated strings to JSON,
    because default encoders chokes on them.
    """
    def default(self, obj):
        if isinstance(obj, Promise):
            return force_text(obj)
        return obj


class LazyJSONEncoder(LazyJSONEncoderMixIn, JSONEncoderForHTML):
    pass
