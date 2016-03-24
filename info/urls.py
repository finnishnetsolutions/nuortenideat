# coding=utf-8

from __future__ import unicode_literals

from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^$', views.TopicDetailFirst.as_view(), name='topic_list'),
    url(r'(?P<pk>\d+)/$', views.TopicDetail.as_view(), name='topic_detail'),
)