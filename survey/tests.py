# coding=utf-8

from __future__ import unicode_literals

from account.factories import UserFactory, DEFAULT_PASSWORD

from content.factories import IdeaFactory
from nuka.test.testcases import TestCase

"""
class SurveyTest(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client.login(username=self.user.username, password=DEFAULT_PASSWORD)
        self.idea = IdeaFactory(owners=[self.user])

    def test_open_create_form(self):
        resp = self.client.get(
            "/fi/idea/{}/osallistuminen/kysely/uusi/".format(self.idea.pk)
        )
        self.assertTemplateUsed(resp, "participation/create_survey_form.html")
        self.assertContains(resp, "Uusi kysely")
        self.assertContains(resp, "Täytä kyselyn perustiedot")
        self.assertContains(resp, "Kieliversiot")
        self.assertContains(resp, "id_title")
        self.assertContains(resp, "id_description")
        self.assertContains(resp, "id_expiration_date")
        self.assertContains(resp, "Tallenna kysely")
"""