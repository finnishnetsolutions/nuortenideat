# coding=utf-8

from __future__ import unicode_literals

from datetime import datetime
import logging
import json
from operator import attrgetter

from django.conf import settings
from django.contrib import messages
from django.contrib.syndication.views import Feed
from django.core.mail.message import EmailMessage
from django.core.urlresolvers import reverse, reverse_lazy
from django.db import transaction
from django.http.response import HttpResponseRedirect, JsonResponse, \
    Http404
from django.shortcuts import redirect, get_object_or_404, render_to_response
from django.template.context import RequestContext
from django.utils import timezone
from django.utils.html import escape
from django.utils.translation import ugettext, get_language, ugettext_lazy as _
from django.views.generic.base import View, RedirectView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.views.generic.list import ListView
from requests.exceptions import ConnectionError
from wkhtmltopdf.views import PDFTemplateView
import requests
from actions.signals import action_performed

from content import perms
from content.forms import PublishIdeaDecisionForm, KuaTransferMembershipReasonForm, \
    KuaTransferBlankForm
from content.perms import CanTransferIdeaToKUAWithoutExtraConfirmation
from content.utils import close_idea_target_gallups
from libs.attachtor import views as attachtor
from libs.attachtor.models.models import UploadGroup
from kuaapi.factories import KuaInitiativeStatus
from kuaapi.models import KuaInitiative
from nkcomments.models import CustomComment
from nkmoderation.utils import get_moderated_form_class
from nkvote.models import Vote, Voter
from nkvote.utils import answered_gallups, answered_options, vote, \
    get_vote, get_votes, set_vote_cookie
from nkwidget.forms import WidgetIdeaForm
from nuka.utils import strip_tags
from nuka.views import PreFetchedObjectMixIn
from organization.models import Organization
from .forms import CreateIdeaForm, CreateQuestionForm, CreateQuestionFormAnon, \
    AdditionalDetailForm, IdeaToPdfForm, IdeaSearchForm, IdeaToPdfFormModifier
from .forms import AttachmentUploadForm
from .models import Idea, Initiative, Question, AdditionalDetail
from .perms import CanVoteIdea
from .pdfprint import BetterPDFTemplateResponse


logger = logging.getLogger(__name__)


class ListAndSearchViewMixIn(object):
    form_class = None
    searchform = None
    
    def get_form_kwargs(self):
        return {}

    def get_queryset(self, queryset=None):
        qs = queryset or super(ListAndSearchViewMixIn, self).get_queryset()
        self.searchform = self.form_class(self.request.GET, **self.get_form_kwargs())
        if self.request.GET and self.searchform.is_valid():
            return self.searchform.filtrate(qs)
        return qs.filter(visibility=Initiative.VISIBILITY_PUBLIC).order_by('-published')

    def get_context_data(self, **kwargs):
        kwargs = super(ListAndSearchViewMixIn, self).get_context_data(**kwargs)
        kwargs['searchform'] = self.searchform
        return kwargs


class ListAndSearchView(ListAndSearchViewMixIn, ListView):
    pass


class IdeaListView(ListAndSearchView):
    paginate_by = 15
    template_name = 'content/initiative_list.html'
    form_class = IdeaSearchForm
    queryset = Idea._default_manager.get_queryset()

    def get_form_kwargs(self):
        kwargs = super(IdeaListView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(IdeaListView, self).get_context_data(**kwargs)

        # Widget form.
        initial = {"language": self.request.LANGUAGE_CODE}
        context["widget_form"] = WidgetIdeaForm(initial=initial)

        # Capitalize language choices.
        choices = context["widget_form"].fields["language"].choices
        capitalized_choices = [(k, v.capitalize()) for k, v in choices]
        context["widget_form"].fields["language"].choices = capitalized_choices

        context["widget_url"] = self.request.build_absolute_uri(reverse("nkwidget"))
        context['rss_url'] = self.request.build_absolute_uri(reverse('content:rss'))
        return context


class IdeaBoxesView(ListView):
    """ Returns only the initiative boxes. Allows sorting. """
    # TODO: Implement all the sorting options as necessary.
    SORT_NEWEST = 0
    SORT_OLDEST = 1
    SORT_MOST_COMMENTS = 2
    SORT_LEAST_COMMENTS = 3
    SORT_MOST_LIKES = 4
    SORT_LEAST_LIKES = 5
    SORT_POPULARITY = 6
    sorting = SORT_NEWEST

    limit = 12

    model = Idea
    paginate_by = 15
    template_name = "content/initiative_boxes.html"

    def set_sorting(self):
        order_by = self.request.GET.get("jarjestys")
        if order_by == "uusin":
            self.sorting = self.SORT_NEWEST
        elif order_by == "suosituin":
            self.sorting = self.SORT_POPULARITY

    def get_queryset(self):
        self.set_sorting()

        queryset = super(IdeaBoxesView, self).get_queryset().filter(
            visibility=Initiative.VISIBILITY_PUBLIC
        )

        if self.sorting == self.SORT_NEWEST:
            queryset = queryset.order_by('-published')
        elif self.sorting == self.SORT_POPULARITY:
            # TODO: Optimointi.
            queryset = sorted(queryset, key=attrgetter("popularity"), reverse=True)

        return queryset[:self.limit]

    def get_context_data(self, **kwargs):
        context = super(IdeaBoxesView, self).get_context_data(**kwargs)
        context["initiatives"] = self.object_list
        return context


class CreateIdeaView(CreateView):
    model = Idea
    form_class = CreateIdeaForm
    template_name = 'content/create_idea_form.html'

    def get_form_kwargs(self):
        kwargs = super(CreateIdeaView, self).get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_initial(self):
        initial = {'owners': [self.request.user, ]}
        if 'organization_id' in self.request.GET:
            org = get_object_or_404(Organization, pk=self.request.GET['organization_id'])
            if org.is_real_organization():
                initial['target_organizations'] = [org, ]
            else:
                initial['target_type'] = org.type
        return initial

    @transaction.atomic()
    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.creator = self.request.user
        obj.save()
        form.save_m2m()

        # action processing
        action_performed.send(sender=form.instance, created=True)

        return HttpResponseRedirect(obj.get_absolute_url())

    def form_invalid(self, form):
        messages.error(self.request, _("Täytä kaikki pakolliset kentät."))
        return super(CreateIdeaView, self).form_invalid(form)


class IdeaDetailView(PreFetchedObjectMixIn, DetailView):
    model = Idea

    def get_context_data(self, **kwargs):
        context = super(IdeaDetailView, self).get_context_data(**kwargs)
        idea = self.get_object()

        if self.request.user.is_authenticated() and self.request.user.is_moderator:
            comments = idea.public_comments()
        else:
            comments = idea.public_comments().public()

        context['comments'] = comments
        context["absolute_uri"] = self.request.build_absolute_uri()
        context["keksit"] = self.request.COOKIES
        context["answered_gallups"] = answered_gallups(self.request)
        context["answered_options"] = answered_options(self.request)
        context["idea_voteable"] = CanVoteIdea(
            request=self.request, obj=idea).is_authorized()
        context["vote"] = get_vote(self.request, Idea, self.kwargs["initiative_id"])
        context["comment_votes"] = get_votes(
            self.request, CustomComment, comments
        )
        return context


class IdeaVoteView(RedirectView):
    choice = Vote.VOTE_NONE
    pattern_name = "content:idea_detail"

    def get_object(self):
        return Idea.objects.get(pk=self.kwargs["initiative_id"])

    def get_redirect_url(self, *args, **kwargs):
        kwargs.pop('obj')
        return super(IdeaVoteView, self).get_redirect_url(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        vote_object = vote(request, Idea, self.get_object(), self.choice)
        # Set the cookie for voting before returning response.
        response = super(IdeaVoteView, self).post(request, *args, **kwargs)
        try:
            voter_id = vote_object.voter.voter_id
        except AttributeError:
            voter_id = None
        # needs to set cookie for request too. permission checks will then have fresh data
        self.request.COOKIES[Voter.VOTER_COOKIE] = voter_id
        return set_vote_cookie(request, response, voter_id)


class IdeaPartialEditView(PreFetchedObjectMixIn, UpdateView):

    # not in use for now
    no_moderation_reason_templates = (
        # 'content/idea_edit_title_form.html',
        # 'content/idea_edit_picture_form.html',
        # 'content/idea_edit_description_form.html',
    )

    def get_form_class(self):
        template = self.kwargs['template_name']
        klass = self.kwargs['form_class']

        if template not in self.no_moderation_reason_templates and \
                not perms.OwnsInitiative(
                    request=self.request, obj=self.get_object()
                ).is_authorized():
            # we are moderating another user's content, mix in ModReasoningMixIn
            return get_moderated_form_class(klass, self.request.user)
        return klass

    def get_template_names(self):
        return [
            self.kwargs['template_name'],
            'content/idea_edit_base_form.html'
        ]

    def form_valid(self, form):
        form.save()
        return JsonResponse({
            'success': True,
            'next': reverse('content:idea_detail_%s' % self.kwargs['fragment'],
                            kwargs={'initiative_id': self.kwargs['initiative_id']})
        })


class IdeaPartialDetailView(IdeaDetailView):
    def get_template_names(self):
        return [self.kwargs['template_name'], ]


class PublishIdeaView(PreFetchedObjectMixIn, View):
    def post(self, request, **kwargs):
        idea = self.get_object()
        idea.status = Idea.STATUS_PUBLISHED
        idea.visibility = Idea.VISIBILITY_PUBLIC
        idea.published = timezone.now()
        idea.save()
        messages.success(request, ugettext("Idea on julkaistu! Voit vielä muokata "
                                           "ideaa, kunnes siihen tulee ensimmäinen "
                                           "kannanotto tai kommentti."))
        return redirect('content:idea_detail', initiative_id=idea.pk)


class IdeaArchiveSwitchMixIn(PreFetchedObjectMixIn):

    def get_success_url(self):
        return reverse('content:idea_detail',
                       kwargs={'initiative_id': self.get_object().pk})

    def change_visibility(self, visibility):
        idea = self.get_object()
        idea.visibility = visibility

        if visibility == Idea.VISIBILITY_ARCHIVED:
            idea.archived = timezone.now()
        else:
            idea.archived = None
        idea.save()


class ArchiveIdeaView(IdeaArchiveSwitchMixIn, View):
    def post(self, request, **kwargs):
        self.change_visibility(Idea.VISIBILITY_ARCHIVED)
        close_idea_target_gallups(self.get_object())
        messages.success(request, ugettext("Idea on arkistoitu."))
        """ Pohjaa. Lisää vastaanottajan email ja kieli.Looppaa joka vastaanottajalle oma.
        send_email(
            _("Idea arkistoitu."),
            "content/email/idea_archived.html",
            {"idea": self.get_object()},
            [],
            None
        )
        """
        return JsonResponse({'location': self.get_success_url()})


class UnArchiveIdeaView(IdeaArchiveSwitchMixIn, View):
    def post(self, request, **kwargs):
        self.change_visibility(Idea.VISIBILITY_PUBLIC)
        messages.success(request, ugettext("Arkistoitu idea on palautettu."))
        return JsonResponse({'location': self.get_success_url()})


class IdeaOwnerEditView(IdeaPartialEditView, IdeaArchiveSwitchMixIn):

    def form_valid(self, form):
        if form.cleaned_data['owners'].count():
            return super(IdeaOwnerEditView, self).form_valid(form)

        form.save()

        """ Archiving the Idea when owners are removed """
        self.change_visibility(Idea.VISIBILITY_ARCHIVED)
        close_idea_target_gallups(self.get_object())
        messages.success(self.request, ugettext("Idea arkistoitiin, koska sillä ei ole "
                                                "enää omistajia."))
        return JsonResponse({
            'location': reverse('content:idea_detail', kwargs={
                'initiative_id': self.kwargs['initiative_id']}),
        })


class DeleteIdeaPictureView(PreFetchedObjectMixIn, View):
    def delete(self, request, **kwargs):
        obj = self.get_object()
        obj.picture.delete()
        obj.picture_alt_text = ''
        obj.save()
        return JsonResponse({'success': True,
                             'next': reverse('content:idea_detail_picture',
                                             kwargs={'initiative_id': obj.pk})})

    def post(self, request, **kwargs):
        return self.delete(request, **kwargs)


class DeleteIdeaView(DeleteView):
    model = Idea
    pk_url_kwarg = "initiative_id"
    template_name = "content/idea_confirm_delete.html"
    success_url = reverse_lazy("content:initiative_list")

    def get_success_url(self):
        messages.success(
            self.request,
            ugettext("Idea '{0}' on poistettu.").format(self.get_object().title)
        )
        return super(DeleteIdeaView, self).get_success_url()


class IdeaAdditionalDetailEditView(CreateView, UpdateView):
    model = AdditionalDetail
    form_class = AdditionalDetailForm
    template_name = 'content/idea_detail_additional_details_add.html'

    def get_context_data(self, **kwargs):
        context = super(IdeaAdditionalDetailEditView, self).get_context_data(**kwargs)
        if self.get_object().pk is not None:
            context['detail_update'] = True
        return context

    def get_object(self, queryset=None):
        if 'additional_detail_id' in self.kwargs:
            return get_object_or_404(self.kwargs['obj'].details,
                                     pk=self.kwargs['additional_detail_id'])
        else:
            return AdditionalDetail(idea=self.kwargs['obj'])

    def form_valid(self, form):
        form.save()
        return JsonResponse({
            'success': True,
            'next': reverse('content:list_details',
                            kwargs={'initiative_id': self.kwargs['obj'].pk})})


class IdeaAdditionalDetailListView(ListView):
    model = None
    template_name = 'content/idea_detail_additional_details_list.html'
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        kwargs['object'] = get_object_or_404(self.model,
                                             pk=self.kwargs[self.pk_url_kwarg])
        return kwargs


class CreateQuestionView(CreateView):
    model = Question
    template_name = 'content/create_question_form.html'

    def get_form_class(self):
        if self.request.user.is_authenticated():
            return CreateQuestionForm
        else:
            return CreateQuestionFormAnon

    def get_organization(self):
        return get_object_or_404(Organization.objects.all(),  # TODO: active
                                 pk=self.kwargs['organization_id'])

    def get_context_data(self, **kwargs):
        context = super(CreateQuestionView, self).get_context_data(**kwargs)
        context['target_organization'] = self.get_organization()
        return context

    @transaction.atomic()
    def form_valid(self, form):
        obj = form.save(commit=False)

        obj.visibility = Question.VISIBILITY_PUBLIC
        obj.published = timezone.now()

        if self.request.user.is_authenticated():
            obj.creator = self.request.user

        obj.save()
        form.save_m2m()
        obj.target_organizations.add(self.get_organization())

        if self.request.user.is_authenticated():
            obj.owners.add(self.request.user)

        # action processing
        action_performed.send(sender=form.instance, created=True)

        return HttpResponseRedirect(obj.get_absolute_url())

    def form_invalid(self, form):
        messages.error(self.request, _("Täytä kaikki pakolliset kentät."))
        return super(CreateQuestionView, self).form_invalid(form)


class QuestionDetailView(PreFetchedObjectMixIn, DetailView):
    model = Question
    template_name = 'content/question_detail.html'

    def get_context_data(self, **kwargs):
        context = super(QuestionDetailView, self).get_context_data(**kwargs)
        question = self.get_object()

        if self.request.user.is_authenticated() and self.request.user.is_moderator:
            comments = question.public_comments()
        else:
            comments = question.public_comments().public()

        context['comments'] = comments
        context["comment_votes"] = get_votes(self.request, CustomComment, comments)
        context['absolute_uri'] = self.request.build_absolute_uri()
        return context


class DeleteQuestionView(DeleteView):
    model = Question
    pk_url_kwarg = "initiative_id"

    def delete(self, request, **kwargs):
        obj = self.get_object()
        organization = obj.target_organizations.first()
        obj.delete()
        messages.success(
            request,
            ugettext('Kysymys "{0}" on poistettu.'.format(obj.title))
        )
        return JsonResponse({
            'location': reverse('organization:detail', kwargs={'pk': organization.pk})
        })

    def post(self, request, **kwargs):
        return self.delete(request, **kwargs)


class QuestionToIdea(RedirectView):
    pattern_name = 'content:idea_detail'

    def post(self, request, *args, **kwargs):
        question = get_object_or_404(Question, pk=self.kwargs['question_id'])
        question_tags = question.tags.all()
        question_owners = question.owners.all()
        question_target_organizations = question.target_organizations.all()
        idea = Idea.objects.create(
            title=question.title,
            description=question.description
        )
        idea.tags = question_tags
        idea.owners = question_owners
        idea.target_organizations = question_target_organizations
        messages.success(self.request, ugettext('Uusi idea luotu kysymyksen pohjalta.'))

        return JsonResponse({
            'location': self.get_redirect_url(initiative_id=idea.pk)
        })


class IdeaToPdf(PDFTemplateView):
    model = Idea
    template_name = 'content/idea_pdf.html'
    response_class = BetterPDFTemplateResponse

    filename = 'nuortenideat_{}.pdf'.format(datetime.now().date())
    show_content_in_browser = False
    cmd_options = {
        'viewport-size': '1280x1024',
        'orientation': 'portrait',
        'enable-internal-links': True,
        'enable-external-links': True,
        'load-media-error-handling': 'ignore',
        'load-error-handling': 'ignore',
    }

    def get_form_class(self):
        if perms.CanTransferIdeaForward(request=self.request,
                                        obj=self.get_object()).is_authorized():
            return IdeaToPdfFormModifier
        else:
            return IdeaToPdfForm

    def get_object(self):
        return get_object_or_404(Idea, pk=self.kwargs['initiative_id'])

    def get_votes_for_comments(self):
        return get_votes(
            self.request, CustomComment, self.get_object().public_comments().public()
        )

    def post(self, request, **kwargs):
        obj = self.get_object()
        form = self.get_form_class()(request.POST, instance=obj)

        if form.is_valid():

            context = super(IdeaToPdf, self).get_context_data(**kwargs)
            context['object'] = obj
            context['comments'] = form.cleaned_data['included_comments']
            context['comment_votes'] = self.get_votes_for_comments()
            context['name'] = form.cleaned_data['name']
            context['contacts'] = form.cleaned_data['contacts']
            context['pdf_mode'] = True

            if form.cleaned_data['included_comments'].count() < \
                    obj.public_comments().public().count():
                context['pdf_comments_hidden'] = True

            resp = self.render_to_response(context)

            if obj.status < Idea.STATUS_TRANSFERRED:
                obj.status = Idea.STATUS_TRANSFERRED
                obj.transferred = timezone.now()
                obj.save()
                if form.cleaned_data['output_method'] \
                        == IdeaToPdfForm.OUTPUT_METHOD_EMAIL:
                    self.save_detail(form, self.create_details_text(form.cleaned_data))
                elif form.cleaned_data.get('additional_detail', False):
                    self.save_detail(form, form.cleaned_data['additional_detail'])

            if form.cleaned_data['output_method'] == IdeaToPdfForm.OUTPUT_METHOD_EMAIL:
                receivers = self.get_email_receivers(form.cleaned_data)
                self.mail_pdf(resp, form.cleaned_data['email_message'], receivers)
                messages.success(request, _("Idea lähetetty sähköpostin liitteenä"))
                return redirect(obj)
            return resp
        else:
            return self.get(request, form=form)

    def save_detail(self, form, detail_text):
        detail_obj = AdditionalDetail(idea=self.get_object())
        detail_obj.detail = detail_text
        detail_obj.type = AdditionalDetail.TYPE_TRANSFERRED
        detail_obj.save()

    def create_details_text(self, cleaned_data):
        org = cleaned_data.get('email_recipient_organization', False)
        if org:
            return "{} / {}".format(org.name, org.admins_str())
        else:
            return cleaned_data.get('email_recipient_name')

    def get_email_receivers(self, cleaned_data):
        # field is deleted in form.clean if it is not needed
        org = cleaned_data.get('email_recipient_organization', None)
        if org:
            receivers = set(map(lambda u: u.email, org.admins.all()))
        # field is deleted in form.clean if it is not needed
        if cleaned_data.get('email_recipient'):
            receivers.add(cleaned_data['email_recipient'])
        if cleaned_data['email_copy']:
            receivers.add(self.request.user.email)
        return receivers

    def get(self, request, *args, **kwargs):
        if kwargs.get('download'):
            return self.render_to_response(self.get_context())
        context = self.get_context()
        context['pdf_preview_mode'] = True
        context['pdf_mode'] = False
        context['form'] = kwargs.get('form') or self.get_form_class()(
            instance=self.get_object())
        return render_to_response(self.template_name, RequestContext(request, context))

    def get_context(self):
        obj = self.get_object()
        context = {
            'object': obj,
            'pdf_preview_mode': False,
            'pdf_mode': True,
            'comments': obj.public_comments().public(),
            'comment_votes': self.get_votes_for_comments(),
        }
        return context

    def mail_pdf(self, resp, msg, receivers):
        tmp_file_html = resp.render_to_temporary_file(template_name=self.template_name,
                                                      delete=False)
        tmp_file = resp.convert_to_pdf(tmp_file_html.name)
        msg = EmailMessage(
            subject=_("Idea liitteenä - nuortenideat.fi"),
            from_email=settings.DEFAULT_FROM_EMAIL,
            body=msg,
            to=receivers
        )
        msg.attach(filename=self.filename, content=tmp_file)
        return msg.send()


class TransferIdeaForwardView(DetailView):
    model = Idea
    pk_url_kwarg = 'initiative_id'
    template_name = 'content/transfer_idea.html'


class TransferIdeaToKUAView(UpdateView):
    model = Idea
    pk_url_kwarg = 'initiative_id'
    template_name = 'content/transfer_idea_to_kua.html'

    def get_object(self, queryset=None):
        return self.kwargs['obj']

    def get_form_class(self):
        perm = CanTransferIdeaToKUAWithoutExtraConfirmation
        if perm(request=self.request, obj=self.kwargs['obj']).is_authorized():
            return KuaTransferBlankForm
        return KuaTransferMembershipReasonForm

    def form_valid(self, form):
        idea = self.get_object()
        # KUA expects municipality codes as integers:
        idea_municipality = int(idea.target_municipality.municipalities.first()
                                .code.lstrip('0'))
        user_municipality = int(self.request.user.settings.municipality.code.lstrip('0'))
        with transaction.atomic():
            data = {
                'municipality': idea_municipality,
                'name': '%s' % idea.title,  # string conversion to use active language
                'proposal': idea.description_plaintext(),
                'extraInfo': None,
                'youthInitiativeId': idea.pk,
                'locale': get_language() or 'fi',
                'contactInfo': {
                    'name': self.request.user.get_full_name(),
                    'municipality': user_municipality,
                    'email': self.request.user.settings.email,
                    'phone': self.request.user.settings.phone_number or None,
                }
            }
            if 'membership' in form.cleaned_data:
                data['contactInfo']['membership'] = form.cleaned_data['membership']

            req = json.dumps(data)

            logger.debug('Submitting to KUA: %s', req)

            try:
                resp = requests.post(settings.KUA_API['create_initiative_url'],
                                     req, headers={'Content-Type': 'application/json',
                                                   'Accept': 'application/json'})
            except ConnectionError as e:
                logger.error("Unable to connect to KUA: %s", req)
                messages.error(self.request, ugettext(
                    "Yhteyden muodostaminen kuntalaisaloite.fi-palveluun "
                    "epäonnistui. Yritä myöhemmin uudelleen.")
                )

            try:
                data = resp.json()
            except ValueError as e:
                data = {'failure': '%s: %s - %s' % (e, resp.status_code, resp.text)}

            if data['failure'] is None:
                result = data['result']
                kua_initiative = KuaInitiative.objects.create(
                    pk=result['initiativeId'],
                    management_url=result['managementLink'],
                    idea=idea,
                    created_by=self.request.user
                )
                kua_initiative.statuses.create(
                    status=KuaInitiativeStatus.STATUS_DRAFT
                )
                idea.status = Idea.STATUS_TRANSFERRED
                idea.transferred = timezone.now()
                idea.save()
                messages.success(self.request, ' '.join([
                    ugettext("Idea on viety kuntalaisaloite.fi-palveluun luonnoksena."),
                    '<a href="%s" target="_blank">%s</a>' % (
                        escape(result['managementLink']),
                        ugettext("Avaa aloite muokattavaksi tästä.")
                    ),
                    ugettext("Muokkauslinkki on lähetetty myös sähköpostiisi %(email)s.")
                    % {'email': self.request.user.settings.email}
                ]))
                logger.info("Idea %d was exported to KUA by %s", idea.pk,
                            self.request.user)
            else:
                logger.error("KUA initiative creation from idea #%d failed: %s\n"
                             "Request: %s",
                             idea.pk, data['failure'], req)
                messages.error(
                    self.request,
                    ugettext("Kuntalaisaloitteen luominen ideasta epäonnistui.")
                )
        return JsonResponse({'reload': True})


class PublishIdeaDecision(FormView):
    template_name = 'content/publish_idea_decision.html'
    form_class = PublishIdeaDecisionForm

    def get_object(self, queryset=None):
        return self.kwargs['obj']

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        form = self.form_class(request.POST)

        if form.is_valid():
            detail_obj = AdditionalDetail(idea=obj)
            detail_obj.detail = form.cleaned_data['additional_detail']
            detail_obj.type = AdditionalDetail.TYPE_DECISION
            detail_obj.save()

        obj.status = Idea.STATUS_DECISION_GIVEN
        obj.decision_given = timezone.now()
        obj.save()
        messages.success(self.request, ugettext("Idean tila päivitetty."))
        return JsonResponse({'reload': True})


class IdeaPremoderationToggleView(View):

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        obj = self.kwargs['obj']
        obj.premoderation = bool(int(kwargs['premoderation_state']))
        obj.save()
        if obj.premoderation:
            messages.success(
                self.request,
                ' '.join([
                    ugettext("Kommenttien esimoderointi on otettu käyttöön."),
                    ugettext("Ideaan lisättävät kommentit menevät palvelun "
                             "moderaattorien hyväksyttäväksi ennen julkaisua.")
                ])
            )
        else:
            messages.success(
                self.request,
                ' '.join([
                    ugettext("Kommenttien esimoderointi on poistettu käytöstä."),
                    ugettext("Ideaan lisättävät kommentit julkaistaan välittömästi.")
                ])
            )
        return JsonResponse({'reload': True})


class UploadAttachmentView(attachtor.UploadAttachmentView):
    form_class = AttachmentUploadForm

    def get_form_kwargs(self):
        kwargs = super(UploadAttachmentView, self).get_form_kwargs()
        kwargs.update({
            'uploader': self.request.user,
            'upload_group': UploadGroup.objects.filter(pk=self.kwargs['upload_group_id'])
                                               .first()
        })
        return kwargs

    def form_invalid(self, form):
        if '__all__' in form.errors:
            error = form.errors['__all__'][0]
        elif 'file' in form.errors:
            error = form.errors['file'][0]
        else:
            error = ugettext("Tiedoston lähetys epäonnistui.")
        return JsonResponse({'error': error})


class IdeaFeed(Feed):
    title = _("Nuortenideat.fi")
    description = _("Seuraa ideoita.")
    link = settings.BASE_URL
    form_class = IdeaSearchForm
    queryset = Idea.objects.get_queryset()

    def get_object(self, request, *args, **kwargs):

        form = self.form_class(request.GET)
        if not form.is_valid():
            raise Http404()
        return form

    def items(self, form):
        qs = self.queryset.filter(visibility=Initiative.VISIBILITY_PUBLIC).\
            order_by('-published')
        return form.filtrate(qs)

    def item_title(self, item):
        return item

    def item_description(self, item):
        return strip_tags('%s' % item.description)

    def item_link(self, item):
        return self.link.rstrip('/') + item.get_absolute_url()
