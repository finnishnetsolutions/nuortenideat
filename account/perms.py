# coding=utf-8

from __future__ import unicode_literals
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext

from libs.permitter import perms

from nuka import perms as nuka

from .models import User


class AccountBasePermission(nuka.BasePermission):
    def __init__(self, **kwargs):
        self.account = kwargs.pop('obj')
        super(AccountBasePermission, self).__init__(**kwargs)
    
    def is_authorized(self):
        return super(AccountBasePermission, self).is_authorized()


class OwnAccount(AccountBasePermission):
    def is_authorized(self):
        return self.user.pk == self.account.pk


class UserEmailSpecified(nuka.BasePermission):
    def get_unauthorized_url(self):
        return reverse('account:settings', kwargs={'user_id': self.request.user.pk})

    def get_unauthorized_message(self):
        return ugettext("Sinun on määriteltävä sähköpostiosoitteesi ennen jatkamista.")

    def is_authorized(self):
        return bool(self.user.settings.email)
    
    
class IsClosed(AccountBasePermission):
    def get_login_url(self):
        return reverse('frontpage')

    def get_unauthorized_message(self):
        return ugettext("Käyttäjäprofiilia ei ole palvelussa.")

    def is_authorized(self):
        return self.account.status == User.STATUS_ARCHIVED


class CanDisconnectSocial(AccountBasePermission):
    def is_authorized(self):
        print len(self.account.password), 'Salasanan pittuus'
        return len(self.account.password) > 0


CanEditUser = perms.And(
    nuka.IsAuthenticated,
    perms.Or(
        OwnAccount,
        nuka.IsAdmin,
        perms.And(
            nuka.IsModerator,
            nuka.ObjectIsParticipant
        )
    )
)

CanViewUser = perms.Or(
    perms.Not(IsClosed),
    nuka.IsModerator,
)
