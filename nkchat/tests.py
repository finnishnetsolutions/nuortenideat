from unittest.case import skipUnless

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase


class FirebaseTestCase(TestCase):
    pass


class FirebaseRulesUploadTestCase(FirebaseTestCase):
    @skipUnless(settings.FIREBASE.get('enabled', False), "Firebase disabled")
    def test_upload(self):
        call_command('update_chat_rules')


class FirebaseUserCleanupTestCase(FirebaseTestCase):
    @skipUnless(settings.FIREBASE.get('enabled', False), "Firebase disabled")
    def test_clean(self):
        call_command('cleanup_chat_users')

    def test_forceful_cleanup(self):
        call_command('cleanup_chat_users', force=True)
