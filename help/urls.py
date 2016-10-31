# coding=utf-8

from __future__ import unicode_literals

from django.conf.urls import patterns, url

from . import views
from .models import Instruction
from slug.decorators import slug_to_object
from slug.views import SlugRedirect

link_slug_pattern = '{0}|{1}'.format(Instruction.TYPE_CONTACT_DETAILS,
                                     Instruction.TYPE_PRIVACY_POLICY)

obj_by_slug = slug_to_object(Instruction)

urlpatterns = patterns('',
    url(r'^$', views.InstructionDetailFirst.as_view(), name='instruction_list'),
    url(r'^(?P<pk>\d+)/$', SlugRedirect.as_view(model=Instruction, permanent=False),
        name='instruction_detail_pk'),
    url(r'^(?P<slug>[\w-]+)/$', obj_by_slug(views.InstructionDetail.as_view()),
        name='instruction_detail'),
    url(r'^linkki/(?P<slug>%s)/$' % link_slug_pattern,
        views.LinkedInstructionRedirectView.as_view(permanent=False),
        name='linked_instruction_redirect'),
)
