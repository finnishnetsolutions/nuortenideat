# coding=utf-8

from __future__ import unicode_literals

from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import get_language

from .settings import CONF


@python_2_unicode_compatible
class MultiLangDict(dict):
    def __getitem__(self, key):
        if key in self:
            return super(MultiLangDict, self).__getitem__(key)

        if CONF['default_language'] in self:
            return self[CONF['default_language']]

        if len(self.values()) > 0:
            return self.values()[0]

        return ''

    def __str__(self):
        return self.__getitem__(get_language())

    def __get_any_value__(self):
        key = get_language()
        value = ''
        if key in self and self['key']:
            value = super(MultiLangDict, self).__getitem__(key)

        if not value:
            if CONF['default_language'] in self:
                value = self[CONF['default_language']]

        if not value and len(self.values()) > 0:
            for v in self.values():
                if v:
                    return v
        return value

    def get_other_languages_values_list(self, key):
        langs = []
        for lang in self.keys():
            if lang == key:
                continue
            if lang in self and self[lang]:
                langs.append(self[lang])
        return langs

