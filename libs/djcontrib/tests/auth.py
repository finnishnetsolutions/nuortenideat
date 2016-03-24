# coding=utf-8

from __future__ import unicode_literals

from unittest.case import TestCase

from ..test.helpers import DummyRequest
from ..auth.decorators import staff_member_required, superuser_required


class DecoratorTestCase(TestCase):
    def setUp(self):
        self.super_req = DummyRequest(staff=False, superuser=True)
        self.staff_req = DummyRequest(staff=True, superuser=False)
        self.auth_req = DummyRequest(authenticated=True, staff=False,
                                superuser=False)
        self.anon_req = DummyRequest(authenticated=False)

    def test_staff_member_required(self):
        @staff_member_required
        def _test_view(request):
            return 'OK!'

        resp = _test_view(self.staff_req)
        self.assertFalse(hasattr(resp, 'status_code'))
        self.assertEqual(resp, 'OK!')

        self.assertEqual(_test_view(self.auth_req).status_code, 302)
        self.assertEqual(_test_view(self.super_req).status_code, 302)
        self.assertEqual(_test_view(self.anon_req).status_code, 302)

    def test_superuser_required(self):
        @superuser_required
        def _test_view(request):
            return 'OK!'

        resp = _test_view(self.super_req)
        self.assertFalse(hasattr(resp, 'status_code'))
        self.assertEqual(resp, 'OK!')

        self.assertEqual(_test_view(self.auth_req).status_code, 302)
        self.assertEqual(_test_view(self.staff_req).status_code, 302)
        self.assertEqual(_test_view(self.anon_req).status_code, 302)
