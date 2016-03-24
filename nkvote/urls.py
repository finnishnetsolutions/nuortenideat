# coding=utf-8

from __future__ import unicode_literals

from django.conf.urls import url, patterns

from libs.djcontrib.utils.decorators import obj_by_pk
from libs.permitter.decorators import check_perm

from content.models import Initiative

from . import views
from .models import Gallup
from .perms import CanAnswerGallup, CanViewGallup, CanCreateGallup, CanDeleteGallup, \
    CanEditGallup, CanOpenGallup, CanCloseGallup


gallup_as_obj = obj_by_pk(Gallup, "gallup_id")
initiative_as_obj = obj_by_pk(Initiative, "initiative_id")

urlpatterns = patterns(
    "",
    url(
        r'^uusi/$',
        initiative_as_obj(check_perm(CanCreateGallup)(views.GallupFormView.as_view())),
        name='create'
    ),
    url(
        r'^(?P<gallup_id>\d+)/muokkaa/$',
        gallup_as_obj(check_perm(CanEditGallup)(views.GallupFormView.as_view())),
        name='edit'
    ),
    url(
        r'^(?P<gallup_id>\d+)/avaa/$',
        gallup_as_obj(check_perm(CanOpenGallup)(
            views.GallupStatusChangeView.as_view(status=Gallup.STATUS_OPEN)
        )),
        name='open'
    ),
    url(
        r'^(?P<gallup_id>\d+)/vastaa/$',
        gallup_as_obj(check_perm(CanAnswerGallup)(views.GallupResultsView.as_view())),
        name='answer'
    ),
    url(
        r'^(?P<gallup_id>\d+)/tulokset/$',
        gallup_as_obj(check_perm(CanViewGallup)(views.GallupResultsView.as_view())),
        name='results'
    ),
    url(
        r'^(?P<gallup_id>\d+)/sulje/$',
        gallup_as_obj(check_perm(CanCloseGallup)(
            views.GallupStatusChangeView.as_view(status=Gallup.STATUS_CLOSED)
        )),
        name='close'
    ),
    url(
        r'^(?P<gallup_id>\d+)/poista/$',
        gallup_as_obj(check_perm(CanDeleteGallup)(views.DeleteGallupView.as_view())),
        name='delete'
    ),
    url(
        r'^lisaa_kysymys/$',
        views.NewGallupQuestionView.as_view(),
        name='get_question'
    ),
    url(
        r'^lisaa_vaihtoehto/$',
        views.NewGallupOptionView.as_view(),
        name='get_option'
    ),
    url(
        r'^(?P<gallup_id>\d+)/tulokset_pdf/$',
        gallup_as_obj(check_perm(CanViewGallup)(views.GallupResultsToPdfView.as_view())),
        name='results_pdf'
    ),
)
