# coding=utf-8

from __future__ import unicode_literals

from django.conf.urls import patterns, url, include

from . import views


urlpatterns = patterns('',
    url('^upload/', include('.'.join(__package__.split('.')[:-1] + ['urls']))),
    url('^blogs/create/', views.CreateBlogView.as_view()),
    url('^blogs/(?P<pk>\d+)/edit/', views.UpdateBlogView.as_view()),
)
