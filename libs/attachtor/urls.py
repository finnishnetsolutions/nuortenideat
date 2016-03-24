# coding=utf-8

from __future__ import unicode_literals

from django.conf.urls import patterns, url

from . import views


urlpatterns = patterns('',
    url('^(?P<upload_group_id>[a-f0-9]{32})(?P<upload_token>[a-f0-9]{32})/$',
        views.UploadAttachmentView.as_view(),
        name='attachtor_file_upload')
)
