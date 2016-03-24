# coding=utf-8

from __future__ import unicode_literals

from httplib import BAD_REQUEST, NOT_FOUND, FORBIDDEN
import json

from django.conf import settings
from django.core.exceptions import ValidationError
from django.http.response import JsonResponse
from django.views.generic.base import View

from kuaapi.models import KuaInitiative, KuaInitiativeStatus


class JsonResponseBadRequest(JsonResponse):
    status_code = BAD_REQUEST

    def __init__(self, error, **kwargs):
        data = {'failure': '%s' % error}
        super(JsonResponseBadRequest, self).__init__(data, **kwargs)


class JsonResponseNotFound(JsonResponseBadRequest):
    status_code = NOT_FOUND


class JsonResponseForbidden(JsonResponseBadRequest):
    status_code = FORBIDDEN


class CreateStatusApiView(View):
    def post(self, request, **kwargs):
        if settings.KUA_API['ip_restriction'] is not None:
            if request.META['REMOTE_ADDR'] not in settings.KUA_API['ip_restriction']:
                return JsonResponseForbidden('Authentication failed')

        try:
            data = json.loads(request.body)
        except ValueError as e:
            return JsonResponseBadRequest(e)

        if not isinstance(data, dict):
            return JsonResponseBadRequest('Unexpected JSON data format')

        try:
            initiative = KuaInitiative.objects.get(idea_id=kwargs['nua_initiative_id'])
        except KuaInitiative.DoesNotExist as e:
            return JsonResponseNotFound(e)

        status = KuaInitiativeStatus(
            kua_initiative=initiative,
            status=data.get('status', None)
        )

        try:
            status.full_clean()
        except ValidationError as e:
            return JsonResponseBadRequest(e)
        status.save()
        return JsonResponse({'failure': None})
