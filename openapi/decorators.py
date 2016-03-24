# coding=utf-8

from __future__ import unicode_literals

from django.template.loader import render_to_string

from rest_framework_swagger.views import Response


def swagger_content_type_hack(view, supported=['application/json', 'application/xml']):
    """
    Nasty view decorator to hack to text/xml support to rest-framework-swagger.
    """
    def _inner(*args, **kwargs):
        resp = view(*args, **kwargs)
        if isinstance(resp, Response):
            if resp.data and 'apis' in resp.data:
                apis = resp.data['apis']
                for api in apis:
                    if 'operations' in api:
                        for op in api['operations']:
                            op['produces'] = supported
        return resp
    return _inner


def swagger_api_description_hack(view):
    """
    Nasty view decorator to hack to long API description to rest-framework-swagger.
    """
    def _inner(*args, **kwargs):
        resp = view(*args, **kwargs)
        if isinstance(resp, Response):
            if resp.data and 'info' in resp.data and 'description' in resp.data['info']:
                resp.data['info']['description'] =\
                    render_to_string('openapi/docs/description.html')
        return resp
    return _inner
