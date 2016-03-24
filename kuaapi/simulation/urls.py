# coding=utf-8

from __future__ import unicode_literals

from django.conf.urls import patterns, include, url

from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = patterns('',
    url('^initiatives/(?P<pk>\d+)/$', views.InitiativeDetailView.as_view(),
        name='initiative_detail'),

    url('^initiatives/(?P<pk>\d+)/edit/$', views.InitiativeEditView.as_view(),
        name='initiative_edit'),

    url('^api/v1/municipalities$', views.MunicipalityListApiView.as_view(),
        name='municipalities_list'),

    url('^services/nua/1.0/create$', csrf_exempt(views.CreateInitivateApiView.as_view()),
        name='create_initiative')
)