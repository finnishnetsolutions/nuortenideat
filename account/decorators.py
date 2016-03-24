# coding=utf-8

from __future__ import unicode_literals

from functools import wraps

from django.shortcuts import get_object_or_404

from .models import Initiative


def user_as_obj(view):
    """Supplies User-object as kwarg `obj` to a view that receives
    ``initiative_id`` as a kwargs."""
    # TODO: DRY vs content.decorators
    @wraps(view)
    def decorate_view(*args, **kwargs):
        kwargs['obj'] = get_object_or_404(Initiative, pk=kwargs['initiative_id'])
        return view(*args, **kwargs)
    return decorate_view
