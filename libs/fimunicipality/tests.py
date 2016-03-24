# coding=utf-8

from __future__ import unicode_literals

from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test.testcases import TestCase
from django.utils import timezone

from .models import Municipality, Restructuring


class SyncTest(TestCase):
    def test_sync(self):
        # TODO: make faster, e.g. add limiting or dont fetch external resources
        self.assertEqual(Municipality.objects.count(), 0)
        call_command('sync_municipalities')
        self.assertTrue(Municipality.objects.count() >= 476)
        self.assertTrue(Restructuring.objects.count() >= 155)

    def test_validate_ok(self):
        today = timezone.now().date()
        mun = Municipality(code='123',
                           oid='123.123.123',
                           name_fi='Test',
                           name_sv='Test',
                           beginning_date=today,
                           expiring_date=today,
                           created_date=today,
                           last_modified_date=today)
        mun.full_clean()

    def test_validate_fail_magic_code_and_oid(self):
        today = timezone.now().date()
        mun = Municipality(code='198',
                           oid='123.123.123',
                           name_fi='Test',
                           name_sv='Test',
                           beginning_date=today,
                           expiring_date=today,
                           created_date=today,
                           last_modified_date=today)
        self.assertRaises(ValidationError, mun.full_clean)

    def test_validate_fail_nonmagic_and_no_oid(self):
        today = timezone.now().date()
        mun = Municipality(code='123',
                           oid=None,
                           name_fi='Test',
                           name_sv='Test',
                           beginning_date=today,
                           expiring_date=today,
                           created_date=today,
                           last_modified_date=today)
        self.assertRaises(ValidationError, mun.full_clean)

