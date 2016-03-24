# coding=utf-8

from __future__ import unicode_literals

from django.conf.urls import patterns, url

from libs.djcontrib.conf.urls import decorated_patterns
from libs.djcontrib.utils.decorators import combo, obj_by_generic_pk, obj_by_pk
from libs.moderation.models import ModeratedObject
from libs.permitter.decorators import check_perm

from nkmoderation.perms import CanFlagObject, CanModerateContent, CanModerateObject

from . import views


moderated_obj_by_pk = obj_by_pk(ModeratedObject, url_kwarg='moderated_object_id')

urlpatterns = decorated_patterns('', combo(obj_by_generic_pk(),
                                           check_perm(CanFlagObject)),
    url(r'^ilmoita-asiaton-sisalto/(?P<content_type_id>\d+)/(?P<object_id>\d+)/$',
        views.FlagContentView.as_view(), name='flag_content'),
) + decorated_patterns('', combo(moderated_obj_by_pk, check_perm(CanModerateObject)),
    url(r'^moderointi/(?P<moderated_object_id>\d+)/hyvaksy/$',
        views.ApproveModeratedObject.as_view(), name='approve_object'),
    url(r'^moderointi/(?P<moderated_object_id>\d+)/poista/$',
        views.RejectModeratedObject.as_view(), name='reject_object'),
    url(r'^moderointi/(?P<moderated_object_id>\d+)/poista/$',
        views.RejectModeratedObject.as_view(), name='reject_object')
) + decorated_patterns('', check_perm(CanModerateContent),
    url(r'^moderointi/(?P<content_type_id>\d+)/(?P<object_id>\d+)/syy/$',
        views.ApproveModeratedObject.as_view(), name='approve_object'),
)
