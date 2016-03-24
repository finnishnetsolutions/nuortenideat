# coding=utf-8

from __future__ import unicode_literals

from django.conf.urls import patterns, url

from . import views
from .models import Instruction

link_slug_pattern = '{0}|{1}'.format(Instruction.TYPE_CONTACT_DETAILS,
                                     Instruction.TYPE_PRIVACY_POLICY)

urlpatterns = patterns('',
    url(r'^$', views.InstructionDetailFirst.as_view(), name='instruction_list'),
    url(r'(?P<pk>\d+)/$', views.InstructionDetail.as_view(), name='instruction_detail'),
    url(r'^linkki/(?P<slug>%s)/$' % link_slug_pattern,
        views.LinkedInstructionRedirectView.as_view(),
        name='linked_instruction_redirect'),
)
