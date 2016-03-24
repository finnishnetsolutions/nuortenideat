# coding=utf-8

from __future__ import unicode_literals


def legacy_json_plaintext(func):
    def _inner(request, *args, **kwargs):
        resp = func(request, *args, **kwargs)
        json_type = 'application/json'
        if resp['Content-Type'].startswith(json_type) \
                and json_type not in request.META.get('Accept', ''):
            resp['Content-Type'] = resp['Content-Type'].replace(json_type, 'text/html')
        return resp
    return _inner
