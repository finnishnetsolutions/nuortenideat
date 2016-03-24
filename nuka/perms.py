# coding=utf-8

from __future__ import unicode_literals
from django.contrib import messages

from django.core.urlresolvers import reverse
from django.http.response import JsonResponse
from django.utils.translation import ugettext_lazy as _

from account.models import GROUP_NAME_MODERATORS, GROUP_NAME_ADMINS

from libs.permitter import perms


class BasePermission(perms.FriendlyRequestPermission):
    unauthorized_message = _("Ei käyttöoikeutta.")

    def __init__(self, **kwargs):
        """Accept arbitrary kwargs, so wer are compatible with any View's kwargs."""
        super(BasePermission, self).__init__(request=kwargs['request'])

    def get_login_url(self):
        return reverse('account:login')

    def get_unauthorized_response(self):
        if self.request.is_ajax():
            messages.error(self.request, self.get_unauthorized_message())
            return JsonResponse({'location': self.get_unauthorized_url()}, safe=False)
        return super(BasePermission, self).get_unauthorized_response()


class IsAuthenticated(BasePermission):
    unauthorized_message = _("Kirjaudu sisään tai rekisteröidy käyttääksesi toimintoa.")

    def is_authorized(self):
        return self.user.is_authenticated()

    def get_login_url(self):
        return reverse('account:login')


class IsModeratorCheck(BasePermission):
    unauthorized_message = _("Toiminto vaatii moderaattorin oikeudet.")

    def is_authorized(self):
        # Admins are always moderators too, for now at least.
        mod_groups = [GROUP_NAME_MODERATORS, GROUP_NAME_ADMINS]
        return len(set(self.user.group_names) & set(mod_groups)) > 0

IsModerator = perms.And(IsAuthenticated, IsModeratorCheck)


class IsAdmin(BasePermission):
    unauthorized_message = _("Toiminto vaatii ylläpitäjän oikeudet.")

    def is_authorized(self):
        admin_groups = [GROUP_NAME_ADMINS]
        return len(set(self.user.group_names) & set(admin_groups)) > 0


class ObjectIsParticipant(BasePermission):
    def __init__(self, **kwargs):
        self.object = kwargs['obj']
        super(ObjectIsParticipant, self).__init__(**kwargs)

    def is_authorized(self):
        return self.object.groups.count() == 0
