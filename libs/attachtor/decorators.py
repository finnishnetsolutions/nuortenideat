# coding=utf-8

from __future__ import unicode_literals

from functools import wraps

from django.http.response import HttpResponseBadRequest

from utils import get_upload_token


def validate_upload_token(view_func=None, id_kw='upload_group_id',
                          token_kw='upload_token'):

    def _outer(func):

        @wraps(func)
        def _inner(request, *args, **kwargs):
            if kwargs[token_kw] != get_upload_token(kwargs[id_kw]):
                return HttpResponseBadRequest('Invalid upload token')
            return func(request, *args, **kwargs)

        return _inner

    return _outer if view_func is None else _outer(view_func)
