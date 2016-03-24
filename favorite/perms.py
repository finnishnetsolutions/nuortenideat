# coding=utf-8

from __future__ import unicode_literals

from django.contrib.contenttypes.models import ContentType

from .models import Favorite
from nuka import perms as nuka


class CanFollow(nuka.BasePermission):

    def __init__(self, **kwargs):
        self.obj = kwargs['obj']
        super(CanFollow, self).__init__(**kwargs)

    def is_authorized(self):
        ct = ContentType.objects.get_for_model(self.obj)
        return not Favorite.objects.filter(object_id=self.obj.pk, content_type_id=ct.pk,
                                           user_id=self.request.user.pk).count()

