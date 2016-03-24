# coding=utf-8

from __future__ import unicode_literals

from django.conf.urls import patterns, url, include

from content.models import Initiative, Idea, Question
from content.perms import CanTransferIdeaForward, CanPublishIdea, \
    CanTransferIdeaToKUAWithoutExtraAction, CanPublishIdeaDecision, CanChangeIdeaSettings, \
    CanArchiveIdea, CanUnArchiveIdea, CanVoteIdea
from content.views import IdeaFeed
from nkcomments import views as nkcomments
from nkvote import views as nkvote
from nkvote.models import Vote

from libs.djcontrib.conf.urls import decorated_patterns
from libs.djcontrib.utils.decorators import combo
from libs.permitter.decorators import check_perm
from libs.djcontrib.utils.decorators import obj_by_pk
from nuka.decorators import legacy_json_plaintext

from nuka.perms import IsAuthenticated

from . import views, forms
from .perms import CanEditInitiative, CanViewIdea, CanDeleteIdea, CanDeleteQuestion, \
    CanCreateIdeaFromQuestion

initiative_as_obj = obj_by_pk(Initiative, 'initiative_id')

IDEA_FRAGMENT_URLS = (
    # (url part, template name/url name part, form_class)
    (r'kuva',           'picture',          forms.EditIdeaPictureForm),
    (r'otsikko',        'title',            forms.EditInitiativeTitleForm),
    (r'kuvaus',         'description',      forms.EditInitiativeDescriptionForm),
    (r'omistajat',      'owners',           forms.EditIdeaOwnersForm,
     views.IdeaOwnerEditView),
    (r'aiheet',         'tags',             forms.EditInitiativeTagsForm),
    (r'organisaatiot',  'organizations',    forms.EditIdeaOrganizationsForm),
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
    url(r'^rss/$', IdeaFeed(), name='rss'),
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
        include("nkvote.urls", namespace="gallup")),
    url(r'kysymykset/uusi/(?P<organization_id>\d+)/$', views.CreateQuestionView.as_view(),
        name='create_question'),
    url(r'ideat/laatikot/$', views.IdeaBoxesView.as_view(),
        name="initiative_boxes"),
) + decorated_patterns('', combo(initiative_as_obj, check_perm(CanVoteIdea)),
     url(r'ideat/(?P<initiative_id>\d+)/kannata/$',
         views.IdeaVoteView.as_view(choice=Vote.VOTE_UP),
         name="support_idea"),
     url(r'ideat/(?P<initiative_id>\d+)/vastusta/$',
         views.IdeaVoteView.as_view(choice=Vote.VOTE_DOWN),
         name="oppose_idea"),
) + decorated_patterns('', initiative_as_obj,
    url(r'kysymykset/(?P<initiative_id>\d+)/$', views.QuestionDetailView.as_view(),
        name='question_detail'),
    url(r'kysymykset/(?P<initiative_id>\d+)/kommentointi/$',
        nkcomments.CommentBlockView.as_view(model=Question,
                                 pk_url_kwarg='initiative_id'),
        name='comment_block_question'),
) + decorated_patterns('', combo(initiative_as_obj,
                                 check_perm(CanViewIdea)),
    url(r'ideat/(?P<initiative_id>\d+)/$', views.IdeaDetailView.as_view(),
        name='idea_detail'),
    url(r'ideat/(?P<initiative_id>\d+)/pdf-lataus/$',
        views.IdeaToPdf.as_view(), kwargs={'download': True},
        name='idea_to_pdf_download'),
    url(r'ideat/(?P<initiative_id>\d+)/kommentointi/$',
        nkcomments.CommentBlockView.as_view(model=Idea,
                                 pk_url_kwarg='initiative_id'),
        name='comment_block_idea'),
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
) + decorated_patterns('', combo(initiative_as_obj,
                                 check_perm(CanEditInitiative)),
   url(r'ideat/(?P<initiative_id>\d+)/poista/kuva/$',
       views.DeleteIdeaPictureView.as_view(), name='delete_idea_picture'),
    *partial_edit_patterns
) + decorated_patterns('', combo(initiative_as_obj,
                                 check_perm(CanDeleteIdea)),
    url(r'ideat/(?P<initiative_id>\d+)/poista/$',
        views.DeleteIdeaView.as_view(), name='delete_idea')
) + decorated_patterns('', combo(initiative_as_obj,
                                 check_perm(CanDeleteQuestion)),
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
) + decorated_patterns('', combo(initiative_as_obj, check_perm(CanTransferIdeaForward)),
    url(r'ideat/(?P<initiative_id>\d+)/pdf-luonti/$',
        views.IdeaToPdf.as_view(), name='idea_to_pdf'),
)
