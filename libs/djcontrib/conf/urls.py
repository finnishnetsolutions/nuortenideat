# coding=utf-8

from __future__ import unicode_literals

from django.core.urlresolvers import RegexURLPattern, RegexURLResolver
from django.conf.urls import patterns


def decorated_patterns(prefix, func, *args):
    class DecoratedMixin(object):
        def resolve(self, *args, **kwargs):
            result = super(DecoratedMixin, self).resolve(*args, **kwargs)
            if result:
                result.func = self._decorate_with(result.func)
            return result

    class DecoratedURLPattern(DecoratedMixin, RegexURLPattern):
        pass

    class DecoratedURLResolver(DecoratedMixin, RegexURLResolver):
        pass

    result = patterns(prefix, *args)

    if func:
        for p in result:
            if isinstance(p, RegexURLPattern):
                p.__class__ = DecoratedURLPattern
                p._decorate_with = func
            elif isinstance(p, RegexURLResolver):
                p.__class__ = DecoratedURLResolver
                p._decorate_with = func

    return result
