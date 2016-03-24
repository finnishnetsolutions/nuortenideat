# coding=utf-8

from __future__ import unicode_literals
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext

from libs.permitter import perms

from nuka import perms as nuka

from .models import User


class OwnAccount(nuka.BasePermission):
    def __init__(self, **kwargs):
        self.account = kwargs.pop('obj')
        super(OwnAccount, self).__init__(**kwargs)

    def is_authorized(self):
        return self.user.pk == self.account.pk


class UserEmailSpecified(nuka.BasePermission):
    def get_unauthorized_url(self):
        return reverse('account:settings', kwargs={'user_id': self.request.user.pk})

    def get_unauthorized_message(self):
        return ugettext("Sinun on määriteltävä sähköpostiosoitteesi ennen jatkamista.")

    def is_authorized(self):
        return bool(self.user.settings.email)
    
    
class IsClosed(nuka.BasePermission):
    def __init__(self, **kwargs):
        self.account = kwargs.pop("obj")
        super(IsClosed, self).__init__(**kwargs)
        
    def is_authorized(self):
        return self.account.status == User.STATUS_ARCHIVED


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