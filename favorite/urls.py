# coding=utf-8

from __future__ import unicode_literals

from django.conf.urls import patterns, url
from libs.djcontrib.conf.urls import decorated_patterns
from libs.djcontrib.utils.decorators import combo, obj_by_generic_pk
from libs.permitter.decorators import check_perm
from libs.djcontrib.utils.decorators import obj_by_pk

from . import views
from nuka.perms import IsAuthenticated
from account.perms import CanEditUser
from account.models import User

urlpatterns = decorated_patterns('', combo(obj_by_generic_pk(),
                                           check_perm(IsAuthenticated)),
    url(r'^seuraa/(?P<content_type_id>\d+)/(?P<object_id>\d+)/$',
        views.AddOrRemoveIdeaView.as_view(), name='add_or_remove_idea'),
) + decorated_patterns('', combo(obj_by_pk(User, 'user_id'), check_perm(CanEditUser)),
    url(r'^(?P<user_id>\d+)/seuratut/muokkaa/(?P<ct_id>\d+)/$',
        views.UserFavoriteEditView.as_view(),
        name='favorite_edit'),
    url(r'^(?P<user_id>\d+)/seuratut/nayta/(?P<ct_id>\d+)/$',
        views.UserFavoriteDetailView.as_view(),
        name='favorite_detail')
)
