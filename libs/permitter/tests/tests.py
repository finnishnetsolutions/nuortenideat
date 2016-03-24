# coding=utf-8

from __future__ import unicode_literals

from django.contrib.auth.models import User, AnonymousUser
from django.core.exceptions import PermissionDenied
from django.http.request import HttpRequest
from django.template.base import Template
from django.template.context import RequestContext

from django.test.testcases import TestCase
from django.test.utils import override_settings

from .perms import CanEditObject, AlwaysAuthorized, AlwaysOrAlways, AlwaysOrNever,\
    NeverOrAlways, NeverOrNever, AlwaysAndAlways, AlwaysAndNever, NeverAndAlways,\
    NeverAndNever, IsAuthenticated, NotNever, NotAlways, NotAlwaysNever, NotNeverAlways,\
    NotNeverNever, NeverPermsWithMessage1, NeverPermsWithMessage2

from ..perms import And, perms_cache
from ..decorators import check_perm


app_package = '.'.join(__package__.split('.')[:-1])


@override_settings(
    INSTALLED_APPS=(__package__, app_package),
    TEMPLATE_CONTEXT_PROCESSORS=('django.contrib.auth.context_processors.auth',
                                 '.'.join([app_package, 'context_processors.permitter']))
)
class TemplateContextTest(TestCase):
    def test_simple_permitted(self):
        tmpl = """
        {% if perm.permitter_test.AlwaysAuthorized %}
            success!
        {% endif %}
        """
        req = HttpRequest()
        req.user = AnonymousUser()
        resp = Template(tmpl).render(RequestContext(req))
        self.assertTrue('success!' in resp)

    def test_simple_not_permitted(self):
        tmpl = """
        {% if not perm.permitter_test.NeverAuthorized %}
            success!
        {% endif %}
        """
        req = HttpRequest()
        req.user = AnonymousUser()
        resp = Template(tmpl).render(RequestContext(req))
        self.assertTrue('success!' in resp)

    def test_missing_required_perm_arguments(self):
        tmpl = """
        {% if perm.permitter_test.CanEditObject %}
            fail
        {% endif %}
        """
        req = HttpRequest()
        req.user = User()
        tmpl, ctx = Template(tmpl), RequestContext(req)
        self.assertRaises(KeyError, lambda: tmpl.render(ctx))

    def test_object_permitted(self):
        tmpl = """
        {% if "editable" in perm.permitter_test.CanEditObject %}
            success!
        {% endif %}
        """
        req = HttpRequest()
        req.user = AnonymousUser()
        resp = Template(tmpl).render(RequestContext(req))
        self.assertTrue('success!' in resp)

    def test_object_not_permitted(self):
        tmpl = """
        {% if "uneditable" in perm.permitter_test.CanEditObject %}
            fail :(
        {% else %}
            success!
        {% endif %}
        """
        req = HttpRequest()
        req.user = AnonymousUser()
        resp = Template(tmpl).render(RequestContext(req))
        self.assertFalse('fail' in resp)
        self.assertTrue('success!' in resp)


class SimplePermTest(TestCase):
    def test_is_authorized(self):
        req = HttpRequest()
        req.user = AnonymousUser()
        self.assertTrue(AlwaysAuthorized(request=req).is_authorized())


class ObjectPermTest(TestCase):
    def test_is_authorized(self):
        self.assertTrue(CanEditObject(request=None, obj='editable').is_authorized())
        self.assertFalse(CanEditObject(request=None, obj='nocando').is_authorized())


class AndOrNotTest(TestCase):
    def test_or(self):
        req = HttpRequest()
        req.user = AnonymousUser()
        self.assertTrue(AlwaysOrAlways(request=req).is_authorized())
        self.assertTrue(AlwaysOrNever(request=req).is_authorized())
        self.assertTrue(NeverOrAlways(request=req).is_authorized())
        self.assertFalse(NeverOrNever(request=req).is_authorized())

    def test_and(self):
        req = HttpRequest()
        req.user = AnonymousUser()
        self.assertTrue(AlwaysAndAlways(request=req).is_authorized())
        self.assertFalse(AlwaysAndNever(request=req).is_authorized())
        self.assertFalse(NeverAndAlways(request=req).is_authorized())
        self.assertFalse(NeverAndNever(request=req).is_authorized())

    def test_not(self):
        req = HttpRequest()
        req.user = AnonymousUser()
        self.assertFalse(NotAlways(request=req).is_authorized())
        self.assertTrue(NotNever(request=req).is_authorized())
        self.assertFalse(NotNeverAlways(request=req).is_authorized())
        self.assertFalse(NotAlwaysNever(request=req).is_authorized())
        self.assertTrue(NotNeverNever(request=req).is_authorized())

    def test_mixed(self):
        req = HttpRequest()
        req.user = AnonymousUser()
        AAAAndAON = And(AlwaysAndAlways, AlwaysOrNever)
        AOAAndAAN = And(AlwaysOrAlways, AlwaysAndNever)
        self.assertTrue(AAAAndAON(request=req).is_authorized())
        self.assertFalse(AOAAndAAN(request=req).is_authorized())


class MultioperandMethodProxyTest(TestCase):
    def test_proxy_unauthorized_message(self):
        p1 = NeverPermsWithMessage1()
        p2 = NeverPermsWithMessage2()
        p1.is_authorized()
        p2.is_authorized()
        self.assertEqual(p1.get_unauthorized_message(), 'NeverPerm1.unauthorized_message')
        self.assertEqual(p2.get_unauthorized_message(), 'NeverPerm2.unauthorized_message')


@override_settings(INSTALLED_APPS=(__package__, app_package))
class DiscoveringTest(TestCase):
    def test_discovered(self):
        for k in ('AlwaysAuthorized', 'NeverAuthorized', 'AlwaysAndAlways',
                  'NeverAndNever', 'WildMixPermission'):
            self.assertTrue(k in perms_cache['permitter_test'])
        self.assertFalse('not_perm' in perms_cache['permitter_test'])
        self.assertFalse('NotPerm' in perms_cache['permitter_test'])


@check_perm(IsAuthenticated)
def testview(request):
    return 'ok!'


class ViewDecoratorTest(TestCase):
    def test_check_perm_permitted(self):
        req = HttpRequest()
        req.user = User()
        self.assertEqual('ok!', testview(req))

    def test_check_perm_not_permitted(self):
        req = HttpRequest()
        req.user = AnonymousUser()
        self.assertRaises(PermissionDenied, lambda: testview(req))
