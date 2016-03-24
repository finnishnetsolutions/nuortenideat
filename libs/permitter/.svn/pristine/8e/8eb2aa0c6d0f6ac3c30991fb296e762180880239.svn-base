# coding=utf-8

from __future__ import unicode_literals

from functools import wraps


def check_perm(perm_class):
    def _wrap(func):
        @wraps(func)
        def _inner(*args, **kwargs):
            perm = perm_class(request=args[0], **kwargs)
            if not perm.is_authorized():
                return perm.get_unauthorized_response()
            return func(*args, **kwargs)
        return _inner
    return _wrap
