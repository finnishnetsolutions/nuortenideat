# coding=utf-8

from django.contrib.auth.models import AnonymousUser


class DummyAuthenticatedUser(object):
    def __init__(self, **kwargs):
        kwargs.setdefault('is_active', True)
        for k,v in kwargs.iteritems():
            setattr(self, k, v)

    def is_authenticated(self):
        return True


class DummyRequest(object):
    def __init__(self, user=None, authenticated=False,
                 superuser=False, staff=False, **extra_attrs):
        if user is None:
            if superuser or staff:
                authenticated = True
            if authenticated:
                self.user = DummyAuthenticatedUser(is_superuser=superuser,
                                                   is_staff=staff)
            else:
                self.user = AnonymousUser()
        else:
            self.user = user
        for k,v in extra_attrs.iteritems():
            setattr(self, k, v)

    def build_absolute_uri(self):
        return '/dummy/'

    def get_full_path(self):
        return '/dummy/'