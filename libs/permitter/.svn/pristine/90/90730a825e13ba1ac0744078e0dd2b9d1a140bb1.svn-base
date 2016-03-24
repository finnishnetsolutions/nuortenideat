# coding=utf-8

from __future__ import unicode_literals

import logging
import traceback

from .perms import perms_cache


logger = logging.getLogger(__package__)  # pylint: disable=invalid-name


class PermCheck(object):
    def __init__(self, cls, request):
        self.cls, self.request = cls, request

    def __bool__(self):
        return self.check()

    def __nonzero__(self):      # Python 2 compatibility
        return type(self).__bool__(self)

    def __contains__(self, item):
        return self.check(obj=item)

    def check(self, **kwargs):
        try:
            return self.cls(request=self.request, **kwargs).is_authorized()
        except Exception as exc:
            logger.error(traceback.format_exc())
            logger.warning("Permission check with %s failed: %s", self.cls.__name__, exc)
            raise


class PermitterLookupDict(object):
    def __init__(self, request, app_label):
        self.request, self.app_label = request, app_label

    def __repr__(self):
        return str(perms_cache[self.app_label])

    def __iter__(self):
        # To fix 'item in perms.someapp' and __getitem__ iteraction we need to
        # define __iter__. See #18979 for details.
        raise TypeError("PermitterLookupDict is not iterable.")

    def __getitem__(self, perm_name):
        if perm_name not in perms_cache[self.app_label]:
            raise NotImplementedError("Permission %s.%s does not exist."
                                      % (self.app_label, perm_name))
        return PermCheck(perms_cache[self.app_label][perm_name], self.request)


class PermitterWrapper(object):
    def __init__(self, request):
        self.request = request

    def __getitem__(self, app_label):
        if app_label not in perms_cache:
            raise NotImplementedError("App %s does not exist." % app_label)
        return PermitterLookupDict(self.request, app_label)

    def __iter__(self):
        raise TypeError("PermitterWrapper is not iterable.")

    def __contains__(self, perm_name):
        """
        Lookup by "someapp" or "someapp.someperm" in perms.
        """
        if '.' not in perm_name:
            # The name refers to module.
            return bool(self[perm_name])
        app_label, perm_name = perm_name.split('.', 1)
        return self[app_label][perm_name]


def permitter(req):
    return {'perm': PermitterWrapper(req)}
