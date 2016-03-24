# coding=utf-8

from __future__ import unicode_literals

from django.conf.urls import patterns, url

from . import views


urlpatterns = patterns(
    "",
    url(r"^$", views.CampaignDetailFirstView.as_view(), name="campaign_list"),
    url(r"^(?P<pk>\d+)/$", views.CampaignDetailView.as_view(), name="campaign_detail"),
)
