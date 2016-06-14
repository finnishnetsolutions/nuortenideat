# coding=utf-8

from __future__ import unicode_literals

from django.utils.translation import override

from libs.attachtor.utils import get_upload_signature

from nuka.test.testcases import TestCase
from account.factories import UserFactory, DEFAULT_PASSWORD
from organization.factories import OrganizationFactory, MunicipalityFactory
from organization.models import Organization
from organization.templatetags.organization import type_name


class CreateOrganizationTest(TestCase):
    def setUp(self):
        # HACK: setup Organization.unmoderated_objects manager
        from libs.moderation.helpers import auto_discover
        auto_discover()

        self.user = UserFactory()
        self.client.login(username=self.user.username,
                          password=DEFAULT_PASSWORD)

    def test_load_create_form(self):
        resp = self.client.get('/fi/organisaatiot/uusi/')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Uusi organisaatio")

    def test_create(self):
        self.assertEqual(Organization.unmoderated_objects.real().count(), 0)
        resp = self.client.post('/fi/organisaatiot/uusi/', {
            'name-fi': 'Test Oy',
            'name-sv': 'Test Ab',
            'type': Organization.TYPE_ORGANIZATION,
            'municipalities': [],
            'admins': [self.user.pk, ],
            'description-fi': 'tadaa',
            'terms_accepted': True,
            'upload_ticket': get_upload_signature()
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Organization.unmoderated_objects.real().count(), 1)
        org = Organization.unmoderated_objects.real().first()

        self.assertEqual('%s' % org.name, 'Test Oy')
        self.assertEqual('%s' % org.description, 'tadaa')
        with override(language='sv'):
            self.assertEqual('%s' % org.name, 'Test Ab')
            self.assertEqual('%s' % org.description, 'tadaa')

        self.assertEqual(len(org.admins.all()), 1)
        self.assertEqual(self.user.pk, org.admins.first().pk)
        self.assertEqual(org.municipalities.count(), 0)
        self.assertFalse(org.is_active)

    def test_create_municipality(self):
        self.assertEqual(Organization.unmoderated_objects.real().count(), 0)
        resp = self.client.post('/fi/organisaatiot/uusi/', {
            'name-sv': 'Test Org',
            'type': Organization.TYPE_MUNICIPALITY,
            'municipalities': [MunicipalityFactory().pk],
            'admins': [self.user.pk, ],
            'description-fi': 'tadaa',
            'description-sv': 'wohoo',
            'terms_accepted': True,
            'upload_ticket': get_upload_signature()
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Organization.unmoderated_objects.real().count(), 1)
        org = Organization.unmoderated_objects.real().first()
        self.assertEqual('%s' % org.name, 'Test Org')
        self.assertEqual('%s' % org.description, 'tadaa')
        with override(language='fi'):
            self.assertEqual('%s' % org.name, 'Test Org')
            self.assertEqual('%s' % org.description, 'tadaa')
        with override(language='sv'):
            self.assertEqual('%s' % org.name, 'Test Org')
            self.assertEqual('%s' % org.description, 'wohoo')
        with override(language='en'):
            self.assertEqual('%s' % org.name, 'Test Org')
            self.assertEqual('%s' % org.description, 'tadaa')
        self.assertEqual(org.municipalities.count(), 1)

    def test_create_municipality_too_many_municipalities(self):
        resp = self.client.post('/fi/organisaatiot/uusi/', {
            'name': 'Test Org',
            'type': Organization.TYPE_MUNICIPALITY,
            'municipalities': [MunicipalityFactory().pk, MunicipalityFactory().pk],
            'admins': [self.user.pk, ],
            'description': 'tadaa'
        })
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Kunta-tyyppisen organisaation täytyy liittyä "
                                  "täsmälleen yhteen kuntaan.")


class OrganizationDetailTest(TestCase):
    def test_organization_detail_visitor(self):
        org = OrganizationFactory()
        resp = self.client.get('/fi/organisaatiot/%d/' % org.pk)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, '<h1 class="h3-style">%s' % org.name)
        self.assertNotContains(resp, 'fa-edit')

    def test_organization_detail_org_admin(self):
        user = UserFactory()
        org = OrganizationFactory(admins=[user, ])
        self.client.login(username=user.username, password=DEFAULT_PASSWORD)
        resp = self.client.get('/fi/organisaatiot/%d/' % org.pk)
        self.assertTemplateUsed(resp, 'organization/organization_detail.html')
        self.assertTemplateUsed(resp, 'organization/organization_detail_description.html')
        self.assertContains(resp, 'fa-edit', count=4)


class OrganizationListTest(TestCase):
    def test_list(self):
        org = OrganizationFactory()
        resp = self.client.get('/fi/organisaatiot/')
        self.assertContains(resp, org.name)


class OrganizationTemplateFilterTest(TestCase):
    def test_type_name(self):
        self.assertEqual(type_name(0), "Tuntematon")
        self.assertEqual(type_name(1), "Koko Suomi")
        self.assertEqual(type_name(3), "Järjestö")
        self.assertEqual(type_name(4), "Kunta")
        self.assertEqual(type_name(5), "Koulu tai muu oppilaitos")
        self.assertEqual(type_name(10), "Muu organisaatio")
        self.assertIsNone(type_name(-1))
