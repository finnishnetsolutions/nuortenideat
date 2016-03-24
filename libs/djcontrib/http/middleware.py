# coding=utf-8

from __future__ import unicode_literals


class XForwardedForMiddleware(object):
    def process_request(self, request):
        if "HTTP_X_FORWARDED_FOR" in request.META:
            ip = request.META["HTTP_X_FORWARDED_FOR"].split(',')[-1].strip()
            request.META["REMOTE_ADDR"] = ip


class NeverCacheMiddleware(object):
    def process_response(self, request, response):
        response['Pragma'] = 'no-cache'
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
        return response


class NoSniffMiddleware(object):
    def process_response(self, request, response):
        response['X-Content-Type-Options'] = 'nosniff'
        return response
