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
