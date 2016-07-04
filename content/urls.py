# coding=utf-8

from __future__ import unicode_literals

from django.conf.urls import patterns, url, include

from nkcomments import views as nkcomments
from nkvote.models import Vote

from libs.djcontrib.conf.urls import decorated_patterns
from libs.djcontrib.utils.decorators import combo
from libs.permitter.decorators import check_perm
from libs.djcontrib.utils.decorators import obj_by_pk
from nuka.decorators import legacy_json_plaintext
from nuka.perms import IsAuthenticated
from survey.models import Survey
from survey.perms import CanEditSurvey
from .survey_perms import CanViewSurvey, CanOpenSurvey, CanCloseSurvey, CanDeleteSurvey, \
    ShowSurveyResults, CanEditSurveyName
from . import views, forms
from .models import Initiative, Idea, Question, IdeaSurvey
from .perms import CanTransferIdeaForward, CanPublishIdea, \
    CanTransferIdeaToKUAWithoutExtraAction, CanPublishIdeaDecision, \
    CanChangeIdeaSettings, CanArchiveIdea, CanUnArchiveIdea, CanVoteIdea, \
    CanCreateSurvey, CanEditInitiative, CanViewIdea, CanDeleteIdea, CanDeleteQuestion, \
    CanCreateIdeaFromQuestion


initiative_as_obj = obj_by_pk(Initiative, 'initiative_id')
survey_as_obj = obj_by_pk(Survey, 'survey_id')

IDEA_FRAGMENT_URLS = (
    # (url part, template name/url name part, form_class)
    (r'kuva',           'picture',          forms.EditIdeaPictureForm,
     views.IdeaPictureEditView),
    (r'otsikko',        'title',            forms.EditInitiativeTitleForm),
    (r'kuvaus',         'description',      forms.EditInitiativeDescriptionForm),
    (r'omistajat',      'owners',           forms.EditIdeaOwnersForm,
     views.IdeaOwnerEditView),
    (r'aiheet',         'tags',             forms.EditInitiativeTagsForm),
    (r'organisaatiot',  'organizations',    forms.EditIdeaOrganizationsForm),
    (r'asetukset',      'settings',         forms.EditIdeaSettingsForm),
)

partial_detail_urls = [
    url(r'ideat/(?P<initiative_id>\d+)/nayta/%s/$' % u[0],
        views.IdeaPartialDetailView.as_view(),
        name='idea_detail_%s' % u[1],
        kwargs={'template_name': 'content/idea_detail_%s.html' % u[1]}
    ) for u in IDEA_FRAGMENT_URLS
]

partial_edit_patterns = [
    url(r'ideat/(?P<initiative_id>\d+)/muokkaa/%s/$' % u[0],
        legacy_json_plaintext((u[3] if len(u) > 3 else views.IdeaPartialEditView).
                              as_view()),
        name='edit_idea_%s' % u[1],
        kwargs={'template_name': 'content/idea_edit_%s_form.html' % u[1],
                'form_class': u[2], 'fragment': u[1]}
    ) for u in IDEA_FRAGMENT_URLS
]

urlpatterns = patterns('',
    url(r'selaa/$', views.IdeaListView.as_view(), name='initiative_list'),
    url(r'^rss/$', views.IdeaFeed(), name='rss'),
    url(r'ideat/uusi/$', check_perm(IsAuthenticated)(views.CreateIdeaView.as_view()),
        name='create_idea'),
    url(r'ideat/muunna-kysymys-ideaksi/(?P<question_id>\d+)/$',
        check_perm(IsAuthenticated)(views.QuestionToIdea.as_view()),
        name='question_to_idea'),
    url(r'ideat/(?P<initiative_id>\d+)/julkaise/$',
        initiative_as_obj(check_perm(CanPublishIdea)(
            views.PublishIdeaView.as_view()
        )),
        name='publish_idea'),
    url(r'ideat/(?P<initiative_id>\d+)/julkaise-idea-ja-kyselyt/$',
        initiative_as_obj(check_perm(CanPublishIdea)(
            views.PublishIdeaAndSurveysView.as_view()
        )),
        name='publish_idea_and_surveys'),
    url(r'idean-kysely/(?P<survey_id>\d+)/kysely/muokkaa/nimi/$',
        survey_as_obj(check_perm(CanEditSurveyName)(
            views.EditIdeaSurveyNameView.as_view()
        )),
        name='survey_edit_name'),
    url(r'ideat/(?P<initiative_id>\d+)/arkistoi/$',
        initiative_as_obj(check_perm(CanArchiveIdea)(
            views.ArchiveIdeaView.as_view()
        )),
        name='archive_idea'),
    url(r'ideat/(?P<initiative_id>\d+)/palauta-arkistoitu-idea/$',
        initiative_as_obj(check_perm(CanUnArchiveIdea)(
            views.UnArchiveIdeaView.as_view()
        )),
        name='unarchive_idea'),
    url(r'^ideat/(?P<initiative_id>\d+)/gallup/',
        include('nkvote.urls', namespace='gallup')),
    url(r'kysymykset/uusi/(?P<organization_id>\d+)/$', views.CreateQuestionView.as_view(),
        name='create_question'),
    url(r'ideat/laatikot/$', views.IdeaBoxesView.as_view(),
        name='initiative_boxes'),
    url(r'idean-kysely/(?P<survey_id>\d+)/kysely/$', survey_as_obj(
        check_perm(CanViewSurvey)(views.SurveyDetailView.as_view())),
        name='survey_detail'),
    url(r'idean-kysely/(?P<survey_id>\d+)/kysely/nayta/nimi/$', survey_as_obj(
        check_perm(CanViewSurvey)(views.IdeaSurveyNameDetailView.as_view())),
        name='idea_survey_name'),
    url(r'ideat/(?P<initiative_id>\d+)/kysely/uusi/$', initiative_as_obj(
        check_perm(CanCreateSurvey)(views.CreateSurvey.as_view())), name='create_survey'),
    url(r'idean-kysely/(?P<survey_id>\d+)/avaa/$', survey_as_obj(
        check_perm(CanOpenSurvey)(views.IdeaSurveyStatusChangeView.as_view(
            status=IdeaSurvey.STATUS_OPEN))), name='survey_open'),
    url(r'idean-kysely/(?P<survey_id>\d+)/sulje/$', survey_as_obj(
        check_perm(CanCloseSurvey)(views.IdeaSurveyStatusChangeView.as_view(
            status=IdeaSurvey.STATUS_CLOSED))), name='survey_close'),
    url(r'idean-kysely/(?P<survey_id>\d+)/poista/$', survey_as_obj(
        check_perm(CanDeleteSurvey)(views.DeleteIdeaSurveyView.as_view())),
        name='survey_delete'),
    url(r'idean-kysely/(?P<survey_id>\d+)/tulokset-pdf/$', survey_as_obj(
        check_perm(ShowSurveyResults)(views.SurveyResultsToPdfView.as_view())),
        name='survey_results'),
) + decorated_patterns('', combo(initiative_as_obj, check_perm(CanVoteIdea)),
     url(r'ideat/(?P<initiative_id>\d+)/kannata/$',
         views.IdeaVoteView.as_view(choice=Vote.VOTE_UP),
         name='support_idea'),
     url(r'ideat/(?P<initiative_id>\d+)/vastusta/$',
         views.IdeaVoteView.as_view(choice=Vote.VOTE_DOWN),
         name='oppose_idea'),
) + decorated_patterns('', initiative_as_obj,
    url(r'kysymykset/(?P<initiative_id>\d+)/$', views.QuestionDetailView.as_view(),
        name='question_detail'),
    url(r'kysymykset/(?P<initiative_id>\d+)/kommentointi/$',
        nkcomments.CommentBlockView.as_view(model=Question,
                                 pk_url_kwarg='initiative_id'),
        name='comment_block_question'),
) + decorated_patterns('', combo(initiative_as_obj, check_perm(CanViewIdea)),
    url(r'ideat/(?P<initiative_id>\d+)/$', views.IdeaDetailView.as_view(),
        name='idea_detail'),
    url(r'ideat/(?P<initiative_id>\d+)/pdf-lataus/$',
        views.IdeaToPdf.as_view(), kwargs={'download': True},
        name='idea_to_pdf_download'),
    url(r'ideat/(?P<initiative_id>\d+)/kommentointi/$',
        nkcomments.CommentBlockView.as_view(model=Idea, pk_url_kwarg='initiative_id'),
        name='comment_block_idea'),
    url(r'ideat/(?P<initiative_id>\d+)/kyselyt/$',
        views.SurveyBlockView.as_view(pk_url_kwarg='initiative_id'),
        name='survey_block_idea'),
    url(r'ideat/(?P<initiative_id>\d+)/uusi-lisatieto/$',
        views.IdeaAdditionalDetailEditView.as_view(model=Idea,
                                                   pk_url_kwarg='initiative_id'),
        name='add_detail'),
    url(r'ideat/(?P<initiative_id>\d+)/muokkaa-lisatieto/(?P<additional_detail_id>\d+)/$',
        views.IdeaAdditionalDetailEditView.as_view(model=Idea,
                                                   pk_url_kwarg='initiative_id'),
        name='edit_detail'),
    url(r'ideat/(?P<initiative_id>\d+)/listaa-lisatiedot/$',
        views.IdeaAdditionalDetailListView.as_view(model=Idea,
                                                   pk_url_kwarg='initiative_id'),
        name='list_details'),
    *partial_detail_urls
) + decorated_patterns('', combo(initiative_as_obj, check_perm(CanEditInitiative)),
    url(r'ideat/(?P<initiative_id>\d+)/muokkaa/$',
        views.IdeaEditView.as_view(), name='edit_idea'),
    url(r'ideat/(?P<initiative_id>\d+)/poista/kuva/$',
        views.DeleteIdeaPictureView.as_view(), name='delete_idea_picture'),
    *partial_edit_patterns
) + decorated_patterns('', combo(initiative_as_obj, check_perm(CanDeleteIdea)),
    url(r'ideat/(?P<initiative_id>\d+)/poista/$',
        views.DeleteIdeaView.as_view(), name='delete_idea')
) + decorated_patterns('', combo(initiative_as_obj, check_perm(CanDeleteQuestion)),
    url(r'kysymys/(?P<initiative_id>\d+)/poista/$',
        views.DeleteQuestionView.as_view(), name='delete_question')
) + decorated_patterns('', combo(obj_by_pk(Initiative, 'question_id'),
                                 check_perm(CanCreateIdeaFromQuestion)),
    url(r'ideat/muunna-kysymys-ideaksi/(?P<question_id>\d+)/$',
        views.QuestionToIdea.as_view(), name='question_to_idea')
) + decorated_patterns('', combo(initiative_as_obj, check_perm(CanTransferIdeaForward)),
    url(r'ideat/(?P<initiative_id>\d+)/vie-eteenpain/$',
        views.TransferIdeaForwardView.as_view(), name='transfer_idea'),
    url(r'ideat/(?P<initiative_id>\d+)/muunna-aloitteeksi/$',
        check_perm(CanTransferIdeaToKUAWithoutExtraAction)(
            views.TransferIdeaToKUAView.as_view()
        ), name='transfer_idea_to_kua')
) + decorated_patterns('', combo(initiative_as_obj, check_perm(CanPublishIdeaDecision)),
    url(r'ideat/(?P<initiative_id>\d+)/kirjaa-paatos/$',
            views.PublishIdeaDecision.as_view(), name='publish_idea_decision')
) + decorated_patterns('', combo(initiative_as_obj, check_perm(CanChangeIdeaSettings)),
    url(r'ideat/(?P<initiative_id>\d+)/esimoderointi/(?P<premoderation_state>(0|1))/$',
       views.IdeaPremoderationToggleView.as_view(), name='toggle_idea_premoderation'),
   url(r'ideat/(?P<initiative_id>\d+)/kommentoinnin-tila/(?P<commenting_state>(0|1))/$',
       views.IdeaCommentingStatusToggleView.as_view(), name='toggle_idea_commenting'),
) + decorated_patterns('', combo(initiative_as_obj, check_perm(CanTransferIdeaForward)),
    url(r'ideat/(?P<initiative_id>\d+)/pdf-luonti/$',
        views.IdeaToPdf.as_view(), name='idea_to_pdf'),
)

urlpatterns += decorated_patterns('', combo(survey_as_obj, check_perm(CanEditSurvey)),
    url(r'idean-kysely/(?P<survey_id>\d+)/kysely/muokkaa/$',
        views.SurveyDetailView.as_view(edit_mode=True), name='survey_edit'),
    url(r'idean-kysely/(?P<survey_id>\d+)/kysely/tulosten_naytto/(?P<value>\d+)/$',
        views.UpdateSurveyShowResults.as_view(), name='survey_set_show_results'),
    url(r'idean-kysely/(?P<survey_id>\d+)/interaktio/(?P<interaction>(1|2))/$',
        views.IdeaSurveyInteractionToggleView.as_view(), name='toggle_survey_interaction'),
)


