# coding=utf-8

from __future__ import unicode_literals

from django.contrib.contenttypes.models import ContentType
from django.db.models.query_utils import Q
from django.http.response import JsonResponse
from django.utils.translation import ugettext as _

from account.utils import get_client_identifier
from libs.moderation.models import MODERATION_STATUS_PENDING
from nuka import perms as nuka

from libs.permitter import perms
from libs.moderation import moderation

from .models import ContentFlag


class ContentTypeIsModeratable(nuka.BasePermission):
    def __init__(self, **kwargs):
        self.content_type_id = kwargs['content_type_id']
        super(ContentTypeIsModeratable, self).__init__(**kwargs)

    def is_authorized(self):
        klass = ContentType.objects.get(pk=self.content_type_id).model_class()
        return klass in moderation._registered_models


class ObjectAlreadyFlaggedByUser(nuka.BasePermission):
    unauthorized_message = _("Olet jo ilmoittanut sisällön asiattomaksi.")

    def __init__(self, **kwargs):
        self.object = kwargs['obj']
        super(ObjectAlreadyFlaggedByUser, self).__init__(**kwargs)

    def get_unauthorized_response(self):
        super(ObjectAlreadyFlaggedByUser, self).get_unauthorized_response()
        return JsonResponse({'reload': True})

    def is_authorized(self):
        ct = ContentType.objects.get_for_model(self.object)
        client_id = get_client_identifier(self.request)
        q = Q(client_identifier=client_id, content_type=ct, object_id=self.object.pk)

        if self.request.user.is_authenticated():
            q = q | Q(flagger=self.request.user, content_type=ct,
                      object_id=self.object.pk)

        return bool(ContentFlag.objects.filter(q).count())


class ObjectModerationStatusIsPending(nuka.BasePermission):
    unauthorized_message = _("Sisältö on jo moderoitu.")

    def __init__(self, **kwargs):
        self.object = kwargs['obj']
        super(ObjectModerationStatusIsPending, self).__init__(**kwargs)

    def get_unauthorized_response(self):
        super(ObjectModerationStatusIsPending, self).get_unauthorized_response()
        return JsonResponse({'reload': True})

    def is_authorized(self):
        return self.object.moderation_status == MODERATION_STATUS_PENDING


CanFlagObject = perms.And(
    ContentTypeIsModeratable,
    perms.Not(ObjectAlreadyFlaggedByUser)
)

CanModerateContent = perms.And(
    nuka.IsAuthenticated,
    nuka.IsModerator
)

CanModerateObject = perms.And(
    CanModerateContent,
    ObjectModerationStatusIsPending
)