# coding=utf-8

from __future__ import unicode_literals

import json
import os

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseBadRequest, JsonResponse, \
    HttpResponseNotAllowed, HttpResponse
from django.views.generic.base import View
from django.views.generic.detail import DetailView

from ..models import KuaInitiative
from .utils import management_key
from ..views import JsonResponseBadRequest


class CreateInitivateApiView(View):
    def post(self, request, **kwargs):
        if request.META.get('HTTP_ACCEPT') != 'application/json':
            return HttpResponseBadRequest('json-request expected')

        data = json.loads(self.request.body)

        for k in ('municipality', 'name', 'proposal', 'youthInitiativeId', 'locale'):
            if not data.get(k, None):
                return JsonResponseBadRequest("%s expected" % k)

        for k in ('municipality', 'name', 'email'):
            if not data['contactInfo'].get(k, None):
                return JsonResponseBadRequest("contactInfo.%s expected" % k)

        if data['municipality'] == data['contactInfo']['municipality']:
            if 'membership' in data['contactInfo']:
                return JsonResponseBadRequest('contactInfo.membership received, despite '
                                              'matching municipality')
        else:
            if 'membership' not in data['contactInfo']:
                return JsonResponseBadRequest('contactInfo.membership not received, '
                                              'despite municipality mismatch')
            if data['contactInfo']['membership'] not in ('community', 'company',
                                                         'property', ):
                return JsonResponseBadRequest('unexpected contactInfo.membership value')

        kua_id = int(data['youthInitiativeId']) + 111

        return JsonResponse({
            'failure': None,
            'result': {'initiativeId': kua_id,
                       'managementLink': settings.BASE_URL.rstrip('/') +
                       reverse('kuaapi:kuasimulation:initiative_edit',
                               kwargs={'pk': kua_id}) + '?management=%s' %
                                                        management_key(kua_id)}
        })


class MunicipalityListApiView(View):
    def get(self, request, *args, **kwargs):
        sample_data = os.path.join([
            os.path.dirname(os.path.dirname(__file__)),
            'testdata', 'municipalities.json'
        ])
        return HttpResponse(sample_data, content_type='application/json')


class InitiativeDetailView(DetailView):
    model = KuaInitiative
    template_name = 'kuaapi/simulation/kuainitiative_detail.html'


class InitiativeEditView(InitiativeDetailView):
    def dispatch(self, request, *args, **kwargs):
        key = request.GET.get('management', '')
        if management_key(int(kwargs['pk'])) != key:
            return HttpResponseNotAllowed('invalid management key')
        return super(InitiativeEditView, self).dispatch(request, *args, **kwargs)
