# coding=utf-8

from __future__ import unicode_literals

from functools import wraps

from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django.utils.functional import SimpleLazyObject


def combo(*decos):
    """Combine multiple decorators into one."""
    def decorate(func):
        decorated = reduce(lambda fun, deco: deco(fun), decos[::-1], func)
        @wraps(func)
        def _inner(*args, **kwargs):
            return decorated(*args, **kwargs)
        return _inner
    return decorate


def obj_by_pk(model, url_kwarg='pk', view_kwarg='obj', model_kwarg='pk', lazy=True):
    """Transforms primary key kwarg from url to an object, and passes it to the view
        as a kwarg."""
    def lookup_obj(view):
        @wraps(view)
        def decorate_view(*args, **kwargs):
            getter = lambda: get_object_or_404(model, **{model_kwarg: kwargs[url_kwarg]})
            kwargs[view_kwarg] = SimpleLazyObject(getter) if lazy else getter()
            return view(*args, **kwargs)
        return decorate_view
    return lookup_obj


def obj_by_generic_pk(content_type_kwarg='content_type_id',
                      object_id_kwarg='object_id',
                      view_kwarg='obj',
                      lazy=True):

    def lookup_obj(view):
        @wraps(view)
        def decorate_view(*args, **kwargs):
            def _look_it_up():
                ct = get_object_or_404(ContentType, pk=kwargs[content_type_kwarg])
                return get_object_or_404(ct.model_class(), pk=kwargs[object_id_kwarg])
            kwargs[view_kwarg] = SimpleLazyObject(_look_it_up) if lazy else _look_it_up()
            return view(*args, **kwargs)
        return decorate_view
    return lookup_obj
