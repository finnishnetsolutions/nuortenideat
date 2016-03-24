# coding=utf-8

from __future__ import unicode_literals

from django.core import mail
from django.test.utils import override_settings
from django.utils.translation import override

from account.factories import UserFactory, DEFAULT_PASSWORD
from content.factories import IdeaFactory

from nuka.test.testcases import TestCase
from nuka.utils import send_email


class AdminTest(TestCase):
    def test_admin_login_redirect(self):
        resp = self.client.get('/fi/admin/')
        self.assertRedirects(resp, '/fi/admin/login/?next=/fi/admin/')


class LocaleRedirectTest(TestCase):
    def test_default_redirect(self):
        resp = self.client.get('/')
        self.assertRedirects(resp, '/fi/', status_code=302)

    def test_swedish_redirect(self):
        user = UserFactory(settings__language='sv')
        self.client.login(username=user.username, password=DEFAULT_PASSWORD)

        resp = self.client.get('/')
        self.assertRedirects(resp, '/sv/', status_code=302)


class IdeaRedirectTest(TestCase):
    def test_idea_redirect(self):
        i = IdeaFactory()
        resp = self.client.get('/ideat/%d/' % i.pk)
        self.assertRedirects(resp, '/fi/ideat/%d/' % i.pk, status_code=302)


class SendEmailTest(TestCase):
    def setUp(self):
        self.recipient = UserFactory()
        self.template = "nuka/tests/email_template.txt"
        self.subject = "Testing this function"
        self.body = "Here is some body text"
        self.language = "fi"

    def send_test_email(self):
        send_email(
            self.subject, self.template, {"body": self.body},
            [self.recipient.settings.email], self.language
        )

    def test_send(self):
        self.assertEqual(len(mail.outbox), 0)
        self.send_test_email()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(len(mail.outbox[0].recipients()), 1)
        self.assertEqual(mail.outbox[0].recipients()[0], self.recipient.settings.email)
        self.assertEqual(mail.outbox[0].subject, self.subject)
        self.assertIn("This text comes from template.", mail.outbox[0].body)
        self.assertIn(self.body, mail.outbox[0].body)
        self.assertFalse('{%' in mail.outbox[0].body)

    @override_settings(BASE_URL="https://www.nuortenideat.fi/")
    def test_signature_fi(self):
        with override("fi"):
            self.language = "fi"
            self.send_test_email()
            self.assertIn("Terveisin,\nNuortenideat.fi", mail.outbox[0].body)
            self.assertIn("https://www.nuortenideat.fi/", mail.outbox[0].body)

    @override_settings(BASE_URL="https://www.nuortenideat.fi/")
    def test_signature_sv(self):
        with override("sv"):
            self.language = "sv"
            self.send_test_email()
            self.assertIn("Hälsningar,\nUngasidéer.fi", mail.outbox[0].body)
            self.assertIn("https://www.ungasideer.fi/", mail.outbox[0].body)

    @override_settings(PRACTICE=True, BASE_URL="https://test.nuortenideat.fi/")
    def test_signature_practice(self):
        self.send_test_email()
        self.assertIn("Nuortenideat.fi (Harjoittelu)", mail.outbox[0].body)
        self.assertIn("https://test.nuortenideat.fi/", mail.outbox[0].body)


class ErrorPageTest(TestCase):

    def test_404(self):
        resp = self.client.get('/fi/ideat/9999/')
        self.assertEquals(resp.status_code, 404, 'status code')
        self.assertTemplateUsed(resp, 'nuka/errors/404.html')