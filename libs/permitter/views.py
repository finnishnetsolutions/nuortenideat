# coding=utf-8

from __future__ import unicode_literals

from . import perms
from .decorators import check_perm


class PermCheckMixIn(object):
    @property
    def check_perm(self):
        raise NotImplementedError('%s does not define attribute check_perm' %
                                  self.__class__.__name__)

    @property
    def check_perms(self):
        return [self.check_perm, ]

    def dispatch(self, *args, **kwargs):
        return check_perm(perms.And(*self.check_perms))(
            super(PermCheckMixIn, self).dispatch
        )(*args, **kwargs)
