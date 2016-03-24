# coding=utf-8

from __future__ import unicode_literals

import json

from django.test import TestCase

from content.factories import IdeaFactory


class ApiTestCase(TestCase):
    def get_json(self, *args, **kwargs):
        kwargs.setdefault('HTTP_ACCEPT', 'application/json')
        resp = self.client.get(*args, **kwargs)
        return json.loads(resp.content)

    def assertContainsKeys(self, data, *keys):  # NOQA
        for key in keys:
            self.assertTrue(key in data, "key '%s' missing from data" % key)

    def assertIsPaginated(self, data):  # NOQA
        return self.assertContainsKeys(data, 'results', 'count', 'next', 'previous')


class IdeaApiTest(ApiTestCase):
    def test_list(self):
        idea = IdeaFactory()
        data = self.get_json('/api/open/0.1/ideas/')
        self.assertIsPaginated(data)
        self.assertEqual(data['results'][0]['title'], idea.title)

    def test_detail(self):
        idea = IdeaFactory()
        data = self.get_json('/api/open/0.1/ideas/%d/' % idea.pk)
        self.assertEqual(data['title'], idea.title)
        self.assertContainsKeys(data, 'webUrl', 'description', 'initiatorOrganization',
                                'targetOrganizations')
