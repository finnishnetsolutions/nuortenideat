# coding=utf-8

from __future__ import unicode_literals
from httplib import BAD_REQUEST

import json
import os

from django.test import TestCase
from django.test.utils import override_settings
from content.factories import IdeaFactory
from content.models import Idea
from kuaapi.factories import ParticipatingMunicipalityFactory, KuaInitiativeFactory, \
    KuaInitiativeStatusFactory
from kuaapi.models import KuaInitiativeStatus
from kuaapi.utils import update_participating_municipalities

from .models import ParticipatingMunicipality

from organization.factories import MunicipalityFactory


class ParticipatingMunicipalityUpdateTest(TestCase):
    def setUp(self):
        # participating (in test json)
        self.m1 = MunicipalityFactory(name_fi='Espoo', code='049')
        self.m2 = MunicipalityFactory(name_fi='Vantaa', code='092')
        self.m3 = MunicipalityFactory(name_fi='Ypäjä', code='981')

        # not participating (in test json)
        self.m4 = MunicipalityFactory(name_fi='Äänekosi', code='992')
        self.m5 = MunicipalityFactory(name_fi='Helsinki', code='091')

    def sample_json(self):
        path = os.path.join(os.path.dirname(__file__), 'testdata', 'municipalities.json')
        return json.loads(open(path).read())

    def test_initial_update(self):
        self.assertEqual(ParticipatingMunicipality.objects.count(), 0)
        update_participating_municipalities(self.sample_json())

        participants = set(
            ParticipatingMunicipality.objects.values_list('municipality__code', flat=True)
        )
        self.assertEqual(ParticipatingMunicipality.objects.count(), 3)
        expected_participants = set(['049', '092', '981'])  # Espoo, Helsinki, Ypäjä
        self.assertEqual(participants, expected_participants)

    def test_some_removed(self):
        ParticipatingMunicipalityFactory(municipality=self.m1)
        ParticipatingMunicipalityFactory(municipality=self.m2)
        ParticipatingMunicipalityFactory(municipality=self.m3)

        # not active in json:
        ParticipatingMunicipalityFactory(municipality=self.m4)
        ParticipatingMunicipalityFactory(municipality=self.m5)

        self.assertEqual(ParticipatingMunicipality.objects.count(), 5)
        update_participating_municipalities(self.sample_json())
        self.assertEqual(ParticipatingMunicipality.objects.count(), 3)
        codes = set(ParticipatingMunicipality.objects.values_list('municipality__code',
                                                                  flat=True))
        expected_codes = set([self.m1.code, self.m2.code, self.m3.code])
        self.assertEqual(codes, expected_codes)

    def test_some_added(self):
        ParticipatingMunicipalityFactory(municipality=self.m1)

        self.assertEqual(ParticipatingMunicipality.objects.count(), 1)
        update_participating_municipalities(self.sample_json())
        self.assertEqual(ParticipatingMunicipality.objects.count(), 3)
        codes = set(ParticipatingMunicipality.objects.values_list('municipality__code',
                                                                  flat=True))
        expected_codes = set([self.m1.code, self.m2.code, self.m3.code])
        self.assertEqual(codes, expected_codes)


class InitiativeStatusApiCallTest(TestCase):
    def test_post_idea_missing(self):
        resp = self.client.post('/api/kua/1.0/initiative/1/status/create/',
                                content_type='application/json',
                                data=json.dumps({'status': 'published'}))
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(json.loads(resp.content)['failure'],
                         "KuaInitiative matching query does not exist.")

    def test_post_kua_initiative_missing(self):
        idea = IdeaFactory()
        resp = self.client.post('/api/kua/1.0/initiative/%d/status/create/' % idea.pk,
                                content_type='application/json',
                                data=json.dumps({'status': 'published'}))
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(json.loads(resp.content)['failure'],
                         "KuaInitiative matching query does not exist.")

    def test_post_published_success(self):
        initiative = KuaInitiativeFactory()
        idea = initiative.idea
        self.assertEqual(idea.status, Idea.STATUS_PUBLISHED)
        resp = self.client.post(
            '/api/kua/1.0/initiative/%d/status/create/' % idea.pk,
            content_type='application/json',
            data=json.dumps({'status': 'published'})
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIsNone(json.loads(resp.content)['failure'])
        self.assertEqual(initiative.statuses.count(), 1)
        initiative.statuses.get(status=KuaInitiativeStatus.STATUS_PUBLISHED)
        # Idea status should not have been updated:
        self.assertIsNone(Idea.objects.get(pk=idea.pk).transferred)
        self.assertEqual(idea.status, Idea.STATUS_PUBLISHED)

    def test_post_decision_given_success(self):
        initiative = KuaInitiativeFactory()
        idea = initiative.idea
        self.assertEqual(initiative.statuses.count(), 0)
        self.assertEqual(idea.status, Idea.STATUS_PUBLISHED)
        self.assertIsNone(idea.decision_given)
        resp = self.client.post(
            '/api/kua/1.0/initiative/%d/status/create/' % idea.pk,
            content_type='application/json',
            data=json.dumps({'status': KuaInitiativeStatus.STATUS_DECISION_GIVEN})
        )
        self.assertEqual(resp.status_code, 200)
        idea = Idea.objects.get(pk=idea.pk)
        self.assertEqual(idea.status, Idea.STATUS_DECISION_GIVEN)
        self.assertIsNotNone(idea.decision_given)
        self.assertEqual(initiative.statuses.count(), 1)
        initiative.statuses.get(status=KuaInitiativeStatus.STATUS_DECISION_GIVEN)

    def test_post_publish_duplicate(self):
        status = KuaInitiativeStatusFactory(
            status=KuaInitiativeStatus.STATUS_PUBLISHED
        )
        initiative = status.kua_initiative
        resp = self.client.post(
            '/api/kua/1.0/initiative/%d/status/create/' % initiative.idea.pk,
            content_type='application/json',
            data=json.dumps({'status': KuaInitiativeStatus.STATUS_PUBLISHED})
        )
        self.assertEqual(resp.status_code, BAD_REQUEST)
        self.assertEqual(
            json.loads(resp.content)['failure'],
            "{'__all__': [u'Kua initiative status jolla on n\\xe4m\\xe4 Kua initiative ja "
            "Status on jo olemassa.']}"
        )

    def test_post_sent_to_municipality(self):
        initiative = KuaInitiativeFactory()
        idea = initiative.idea
        resp = self.client.post(
            '/api/kua/1.0/initiative/%d/status/create/' % idea.pk,
            content_type='application/json',
            data=json.dumps({'status': 'sent-to-municipality'})
        )
        self.assertEqual(resp.status_code, 200)
        idea = Idea.objects.get(pk=idea.pk)
        self.assertEqual(idea.status, Idea.STATUS_PUBLISHED)
        self.assertEqual(idea.kua_initiative.statuses.count(), 1)
        self.assertEqual(idea.kua_initiative.statuses.first().status,
                         KuaInitiativeStatus.STATUS_SENT_TO_MUNICIPALITY)

    def test_post_unknown_status(self):
        status = KuaInitiativeStatusFactory(
            status=KuaInitiativeStatus.STATUS_PUBLISHED
        )
        initiative = status.kua_initiative
        resp = self.client.post(
            '/api/kua/1.0/initiative/%d/status/create/' % initiative.idea.pk,
            content_type='application/json',
            data=json.dumps({'status': 'decision given'})
        )
        self.assertEqual(resp.status_code, BAD_REQUEST)
        self.assertEqual(
            json.loads(resp.content)['failure'],
             "{'status': [u\"Arvo u'decision given' ei kelpaa.\"]}"
        )

    def test_urlencoded_post(self):
        initiative = KuaInitiativeFactory()
        resp = self.client.post(
            '/api/kua/1.0/initiative/%d/status/create/' % initiative.idea.pk,
            data={'status': 'decision-given'}
        )
        self.assertEqual(resp.status_code, BAD_REQUEST)
        self.assertEqual(json.loads(resp.content)['failure'],
                         'No JSON object could be decoded')

    def test_post_bad_json_object(self):
        initiative = KuaInitiativeFactory()
        resp = self.client.post(
            '/api/kua/1.0/initiative/%d/status/create/' % initiative.idea.pk,
            content_type='application/json',
            data=json.dumps("decision-given")
        )
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(json.loads(resp.content)['failure'],
                         'Unexpected JSON data format')


class InitiativeStatusIpRestrictionTest(TestCase):
    def valid_post(self, from_ip):
        initiative = KuaInitiativeFactory()
        idea = initiative.idea
        self.assertEqual(idea.status, Idea.STATUS_PUBLISHED)
        resp = self.client.post(
            '/api/kua/1.0/initiative/%d/status/create/' % idea.pk,
            content_type='application/json',
            data=json.dumps({'status': 'published'}),
            REMOTE_ADDR=from_ip
        )
        return resp

    @override_settings(KUA_API={'ip_restriction': None})
    def test_allow_any(self):
        resp = self.valid_post('123.123.123.123')
        self.assertEqual(resp.status_code, 200)

    @override_settings(KUA_API={'ip_restriction': ('122.122.122.122', '133.133.133.133')})
    def test_deny_wrong_ip(self):
        resp = self.valid_post('123.123.123.123')
        self.assertEqual(resp.status_code, 403)

    @override_settings(KUA_API={'ip_restriction': ('122.122.122.122', '133.133.133.133')})
    def test_valid_ip(self):
        resp = self.valid_post('133.133.133.133')
        self.assertEqual(resp.status_code, 200)
