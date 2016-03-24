# coding=utf-8

from __future__ import unicode_literals

from .. import perms


class AlwaysAuthorized(perms.RequestPermission):
    def is_authorized(self):
        return True


class NeverAuthorized(perms.RequestPermission):
    def is_authorized(self):
        return False


class CanEditObject(perms.BasePermission):
    def __init__(self, *args, **kwargs):
        self.object = kwargs['obj']

    def is_authorized(self):
        return self.object == 'editable'


class IsAuthenticated(perms.RequestPermission):
    def is_authorized(self):
        return self.user.is_authenticated()

# pylint: disable=invalid-name
AlwaysOrAlways = perms.Or(AlwaysAuthorized, AlwaysAuthorized)
AlwaysOrNever = perms.Or(AlwaysAuthorized, NeverAuthorized)
NeverOrAlways = perms.Or(NeverAuthorized, AlwaysAuthorized)
NeverOrNever = perms.Or(NeverAuthorized, NeverAuthorized)

AlwaysAndAlways = perms.And(AlwaysAuthorized, AlwaysAuthorized)
AlwaysAndNever = perms.And(AlwaysAuthorized, NeverAuthorized)
NeverAndAlways = perms.And(NeverAuthorized, AlwaysAuthorized)
NeverAndNever = perms.And(NeverAuthorized, NeverAuthorized)

NotAlways = perms.Not(AlwaysAuthorized)
NotNever = perms.Not(NeverAuthorized)
NotNeverAlways = perms.Not(NeverAuthorized, AlwaysAuthorized)
NotAlwaysNever = perms.Not(AlwaysAuthorized, NeverAuthorized)
NotNeverNever = perms.Not(NeverAuthorized, NeverAuthorized)
NotAlwaysAlways = perms.Not(AlwaysAuthorized, AlwaysAuthorized)


WildMixPermission = perms.And(perms.Or(AlwaysOrNever, NeverAndNever, NeverOrAlways),
                              perms.And(NeverAndAlways, NeverOrAlways),
                              IsAuthenticated)
# pylint: enable=invalid-name


class NeverPerm1(perms.FriendlyRequestPermission):
    unauthorized_message = 'NeverPerm1.unauthorized_message'

    def is_authorized(self):
        return False


class NeverPerm2(NeverPerm1):
    unauthorized_message = 'NeverPerm2.unauthorized_message'


# pylint: disable=invalid-name
NeverPermsWithMessage1 = perms.And(AlwaysAuthorized, NeverPerm1, NeverPerm2)
NeverPermsWithMessage2 = perms.And(NeverPerm2, NeverPerm1)
# pylint: enable=invalid-name


class NotPerm(object):
    pass


def not_perm():
    pass
