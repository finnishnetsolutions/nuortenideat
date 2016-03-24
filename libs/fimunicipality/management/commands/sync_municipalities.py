# coding=utf-8

from __future__ import unicode_literals

from operator import itemgetter
import tempfile

from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import transaction

from suds import client


class Client(client.Client):
    # Ugly copy-paste workaround for https://fedorahosted.org/suds/ticket/376.

    def __init__(self, url, **kwargs):
        options = client.Options()
        options.transport = client.HttpAuthenticated()
        self.options = options
        options.cache = client.ObjectCache(tempfile.mkdtemp(prefix='suds-'))
        self.set_options(**kwargs)
        reader = client.DefinitionsReader(options, client.Definitions)
        self.wsdl = reader.open(url)
        plugins = client.PluginContainer(options.plugins)
        plugins.init.initialized(wsdl=self.wsdl)
        self.factory = client.Factory(self.wsdl)
        self.service = client.ServiceSelector(self, self.wsdl.services)
        self.sd = []
        for s in self.wsdl.services:
            sd = client.ServiceDefinition(self.wsdl, s)
            self.sd.append(sd)
        self.messages = dict(tx=None, rx=None)


def _decode_str(v):
    return unicode(v.encode('utf-8'), 'utf-8')


def _attr_key_value(attr):
    k = _decode_str(attr['_type'])
    v = _decode_str(attr['value']) if 'value' in attr else None
    return k, v


DATA_TO_MODEL_FIELDS = {
    'code': 'code',
    'oid': 'oid',
    'begindate': 'beginning_date',
    'expirationdate': 'expiring_date',
    'createddate': 'created_date',
    'lastmodifieddate': 'last_modified_date',
    'shortname': 'name_fi',
    'Kortnamn': 'name_sv',
}


class Command(BaseCommand):
    @transaction.atomic()
    def handle(self, *args, **options):
        conf = apps.get_app_config('fimunicipality')
        Municipality = conf.get_model('Municipality')
        Restructuring = conf.get_model('Restructuring')

        client = Client(conf.wsdl_url, location=conf.wsdl_url.split('?')[0])
        term_system = client.factory.create('TermSystem')
        term_system._id = conf.code_system_id

        codes = client.service.ListCodes(term_system)
        assert len(codes) == 1, "Unexpected response"
        municipalities = map(lambda m: dict(map(_attr_key_value, m.attribute), code=m._id), codes[0])
        restructurings = {}

        for mun in municipalities:
            data = dict([(v, itemgetter(k)(mun)) for k,v in DATA_TO_MODEL_FIELDS.iteritems()])

            if data['oid'] is None:
                lookup_kwargs = {'code': data['code'],
                                 'oid__isnull': True}
            else:
                lookup_kwargs = {'oid': mun['oid']}

            obj, created = Municipality.objects.update_or_create(
                defaults=data, **lookup_kwargs
            )
            obj.full_clean()

            if mun.get('Korvaava_koodi', None):
                restructurings[obj] = map(lambda s: s.strip(),
                                          mun['Korvaava_koodi'].split(','))

        for mun, new_codes in restructurings.iteritems():
            new_muns = [Municipality.objects.get(code=code) for code in new_codes]
            up_to_date_restructurings = []
            for obj in new_muns:
                rs, created = mun.new_municipalities.update_or_create(
                    new_municipality=obj,
                    defaults={
                        'new_code': obj.code,
                        'old_code': mun.code,
                        'old_municipality': mun
                    }
                )
                up_to_date_restructurings.append(rs.pk)
            mun.new_municipalities.exclude(pk__in=up_to_date_restructurings).delete()
            assert mun.new_municipalities.count() == len(new_codes),\
                "Unxpected number of new municipalities for %s" % mun.oid
