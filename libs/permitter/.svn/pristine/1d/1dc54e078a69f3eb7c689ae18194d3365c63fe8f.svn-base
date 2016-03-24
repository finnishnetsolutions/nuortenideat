# coding=utf-8

from __future__ import unicode_literals

from operator import attrgetter

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _


class MinimalPermission(object):
    def is_authorized(self):
        raise NotImplementedError()


class BasePermission(MinimalPermission):  # pylint: disable=abstract-method
    unauthorized_exception_class = PermissionDenied
    unauthorized_message = _("Permission denied")

    def get_unauthorized_message(self):
        return self.unauthorized_message

    def get_unauthorized_response(self):
        raise self.unauthorized_exception_class(
            self.get_unauthorized_message()
        )


class RequestPermission(BasePermission):  # pylint: disable=abstract-method
    def __init__(self, request=None):
        self.request = request
        self._user = None

    @property
    def user(self):
        if self._user is None:
            self._user = self.request.user
        return self._user


class FriendlyRequestPermission(RequestPermission):  # pylint: disable=abstract-method
    """Redirect to login page with an error message,
     instead of raising PermissionDenied"""

    def get_unauthorized_url(self):
        return self.get_login_url()

    def get_login_url(self):
        return settings.LOGIN_URL

    def get_unauthorized_response(self):
        messages.error(self.request, self.get_unauthorized_message())
        if not self.user.is_authenticated():
            return redirect_to_login(self.request.path,
                                     login_url=self.get_login_url())
        return redirect(self.get_unauthorized_url(), permanent=False)


class MultiOperandPermission(MinimalPermission):  # pylint: disable=abstract-method
    def __init__(self, *args, **kwargs):
        self.perms = [perm(*args, **kwargs) for perm in self.__class__.perm_classes]
        self._failed_perms = []

    def __getattr__(self, item):
        """Magically proxy unimplemented attributes to sub-permissions."""
        # HACKy: unauthorized-attributes proxied to failed perms only
        perms = self._failed_perms if 'unauthorized' in item else self.perms
        for perm in perms:
            if hasattr(perm, item):
                return getattr(perm, item)
        raise AttributeError("Unknown attribute '%s'" % item)

    def check_subperms(self, wanted_result, match_any=False):
        del self._failed_perms[:]
        passes = 0
        for perm in self.perms:
            if perm.is_authorized() is not wanted_result:
                self._failed_perms.append(perm)
                if match_any is False:
                    return False
            else:
                passes += 1
        return passes >= 1


class OrPermission(MultiOperandPermission):
    def is_authorized(self):
        return self.check_subperms(wanted_result=True, match_any=True)


class AndPermission(MultiOperandPermission):
    def is_authorized(self):
        return self.check_subperms(wanted_result=True, match_any=False)


class NotPermission(MultiOperandPermission):
    def is_authorized(self):
        return self.check_subperms(wanted_result=False, match_any=False)


def Or(*perms):  # pylint: disable=invalid-name
    return type(str('Or'.join(map(attrgetter('__name__'), perms))),
                (OrPermission,), {'perm_classes': perms})


def And(*perms):  # pylint: disable=invalid-name
    return type(str('And'.join(map(attrgetter('__name__'), perms))),
                (AndPermission,), {'perm_classes': perms})


def Not(*perms, **kwargs):  # pylint: disable=invalid-name
    """Not(perm1, perm2, ...) == Not(Or(perm1, perm2, ...))"""
    return type(str('Not' + 'Or'.join(map(attrgetter('__name__'), perms))),
                (NotPermission,), {'perm_classes': perms})


perms_cache = {}  # pylint: disable=invalid-name
