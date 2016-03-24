# coding=utf-8

from django.contrib.contenttypes.models import ContentType

import json

from nuka.test.testcases import TestCase
from nkmoderation.models import ContentFlag
from content.factories import IdeaFactory
from content.models import Idea

from libs.moderation.models import ModeratedObject, MODERATION_STATUS_PENDING


class FlaggingTest(TestCase):
    def test_flag_form(self):
        idea = IdeaFactory()
        ct = ContentType.objects.get_for_model(idea)
        resp = self.client.get('/fi/ilmoita-asiaton-sisalto/%d/%d/' % (ct.pk, idea.pk))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'nkmoderation/flag_content_form.html')
        self.assertContains(resp, 'Syy')

    def test_flag_idea(self):
        idea = IdeaFactory()
        ct = ContentType.objects.get_for_model(Idea)

        self.assertEqual(ModeratedObject.objects.filter(
            moderation_status=MODERATION_STATUS_PENDING
        ).count(), 0)

        self.assertEqual(ContentFlag.objects.count(), 0)
        resp = self.client.post('/fi/ilmoita-asiaton-sisalto/%d/%d/' % (ct.pk, idea.pk), {
            'reason': 'i dont like it, put it away'
        })

        self.assertEqual(resp.status_code, 200)
        self.assertTrue(json.loads(resp.content))
        self.assertEqual(ContentFlag.objects.count(), 1)
        flag = ContentFlag.objects.first()
        self.assertEqual(flag.content_object, idea)
        self.assertEqual(ModeratedObject.objects.filter(
            moderation_status=MODERATION_STATUS_PENDING
        ).count(), 1)
