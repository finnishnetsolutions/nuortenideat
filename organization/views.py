# coding=utf-8

from __future__ import unicode_literals
from django.contrib.contenttypes.models import ContentType

from django.core.urlresolvers import reverse
from django.contrib import messages
from django.db import transaction
from django.db.models.query_utils import Q
from django.http.response import JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext, ugettext_lazy as _
from django.views.generic.base import View, TemplateView

from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView, FormView
from django.views.generic.list import ListView
from cropping.views import CropPictureView, EditCroppablePictureView

from .models import Organization

from content.models import Idea, Question, Initiative
from nuka.views import PreFetchedObjectMixIn, ExportView
from organization.forms import CreateOrganizationForm, OrganizationSearchForm, \
    OrganizationSearchFormAdmin, EditPictureForm, CropPictureForm, \
    OrganizationDetailIdeaListForm
from organization.perms import CanEditOrganization


class OrganizationListView(ListView):
    paginate_by = 20
    model = Organization
    template_name = 'organization/organization_list.html'
    searchform = None
    form_class = None

    def get_form_kwargs(self):
        return {'user': self.request.user}

    def get_form_class(self):
        user = self.request.user
        if user.is_authenticated() and (user.is_moderator or user.organizations):
            return OrganizationSearchFormAdmin
        return OrganizationSearchForm

    def get_queryset(self):
        self.form_class = self.get_form_class()
        self.searchform = self.form_class(
            self.request.GET, **self.get_form_kwargs()
        )
        if self.request.GET and self.searchform.is_valid():
            if self.form_class == OrganizationSearchFormAdmin:
                qs = Organization.unmoderated_objects.normal_and_inactive()
            else:
                qs = Organization.objects.normal()
            return self.searchform.filtrate(qs)
        return Organization.objects.normal().order_by('-created')

    def get_context_data(self, **kwargs):
        kwargs = super(OrganizationListView, self).get_context_data(**kwargs)
        kwargs['searchform'] = self.searchform
        return kwargs


class CreateOrganizationView(CreateView):
    model = Organization
    form_class = CreateOrganizationForm
    template_name = 'organization/create_organization.html'

    def get_initial(self):
        return {'admins': [self.request.user, ]}

    def form_invalid(self, form):
        messages.error(self.request, _("Täytä kaikki pakolliset kentät."))
        return super(CreateOrganizationView, self).form_invalid(form)


class OrganizationDetailBaseView(PreFetchedObjectMixIn):
    form_class = OrganizationDetailIdeaListForm

    def get_form_kwargs(self):
        kwargs = {
            'is_admin': CanEditOrganization(request=self.request,
                                            obj=self.get_object()).is_authorized(),
        }
        return kwargs

    def get_default_search_params(self):
        return Q(Q(initiator_organization=self.get_object()) |
                 Q(target_organizations=self.get_object()))

    def get_initiatives(self):
        # If the user can edit the organization, show all their initiatives.
        if CanEditOrganization(request=self.request,
                               obj=self.get_object()).is_authorized():
            qs = Initiative.objects.filter(self.get_default_search_params()).\
                order_by("-created").distinct()
        # If the user cannot edit the organization, only show public initiatives.
        else:
            qs = Initiative.objects.filter(
                Q(visibility=Initiative.VISIBILITY_PUBLIC),
                self.get_default_search_params()
            ).order_by("-published").distinct()
        return qs

    def get_ideas(self):
        if CanEditOrganization(request=self.request,
                               obj=self.get_object()).is_authorized():
            qs = Idea.objects.filter(self.get_default_search_params()).\
                order_by("-created").distinct()
        # only get public ideas.
        else:
            qs = Idea.objects.filter(
                Q(visibility=Initiative.VISIBILITY_PUBLIC),
                self.get_default_search_params()
            ).order_by("-published").distinct()
        return qs


class OrganizationDetailView(OrganizationDetailBaseView, DetailView):
    model = Organization

    def get_context_data(self, **kwargs):
        context = super(OrganizationDetailView, self).get_context_data(**kwargs)
        context["initiatives_list"] = self.get_initiatives()
        context['ideas_count'] = context['initiatives_list'].exclude(
            polymorphic_ctype_id=ContentType.objects.get_for_model(Question).pk).count()
        context['question_count'] = context['initiatives_list'].exclude(
            polymorphic_ctype_id=ContentType.objects.get_for_model(Idea).pk).count()
        context['form'] = self.form_class(**self.get_form_kwargs())
        return context


class OrganizationIdeaList(OrganizationDetailBaseView, ExportView):
    template_name = 'content/initiative_boxes_list.html'

    def get_context_data(self, **kwargs):
        context = super(OrganizationIdeaList, self).get_context_data(**kwargs)
        search_form = self.form_class(self.request.GET, **self.get_form_kwargs())
        qs = self.get_initiatives()

        status = self.request.GET['status'] if 'status' in self.request.GET else None
        if status:
            status_field = search_form.STATUS_FIELD_MAP[int(status)]

            # only ideas have status field
            if status_field == search_form.FIELD_STATUS:
                qs = self.get_ideas()

        if search_form.is_valid():
            qs = search_form.filter(qs)
        context['initiatives'] = qs
        return context


class OrganizationPartialDetailView(OrganizationDetailView):
    def get_template_names(self):
        return [self.kwargs['template_name'], ]


class OrganizationPartialEditView(PreFetchedObjectMixIn, UpdateView):
    def get_form_class(self):
        return self.kwargs['form_class']

    def get_template_names(self):
        return [
            self.kwargs['template_name'],
            'organization/organization_edit_base_form.html'
        ]

    def form_valid(self, form):
        form.save()
        return JsonResponse({
            'success': True,
            'next': reverse(
                'organization:organization_detail_%s' % self.kwargs['fragment'],
                kwargs={'pk': self.kwargs['pk']}
            )
        })


class PictureUpdateView(UpdateView):
    def form_valid(self, form):
        super(PictureUpdateView, self).form_valid(form)
        return JsonResponse({'success': True,
                             'next': self.get_success_url()})

    def get_success_url(self):
        return reverse('organization:picture',
                       kwargs={'pk': self.kwargs['obj'].pk})


class EditPictureView(PreFetchedObjectMixIn, PictureUpdateView, EditCroppablePictureView):
    template_name = 'organization/organization_picture_form.html'
    form_class = EditPictureForm


class CropProfilePictureView(PreFetchedObjectMixIn, PictureUpdateView, CropPictureView):
    form_class = CropPictureForm


class PictureView(PreFetchedObjectMixIn, DetailView):
    template_name = 'organization/organization_detail_picture.html'


class DeletePictureView(View):
    def delete(self, request, **kwargs):
        obj = get_object_or_404(Organization, pk=kwargs['pk'])
        obj.original_picture.delete()
        obj.picture.delete()
        obj.cropping = ''
        obj.save()

        return JsonResponse({'success': True,
                             'next': reverse('organization:picture',
                                             kwargs={'pk': obj.pk})})

    def post(self, request, **kwargs):
        return self.delete(request, **kwargs)


class OrganizationSetActiveMixIn(PreFetchedObjectMixIn):
    def get_success_url(self):
        return self.get_object().get_absolute_url()

    def set_active(self, active=True):
        question = self.get_object()
        question.is_active = active
        question.save()


class OrganizationSetActiveView(OrganizationSetActiveMixIn, View):
    active = True

    def post(self, request, **kwargs):
        self.set_active(self.active)
        if self.active:
            messages.success(request, ugettext("Organisaatio on aktivoitu."))
        return JsonResponse({'location': self.get_success_url()})


class OrganizationArchiveView(OrganizationSetActiveMixIn, View):
    def post(self, request, **kwargs):
        self.set_active(active=False)
        organization = self.get_object()
        organization.admins.clear()
        messages.success(request, ugettext("Organisaatio on arkistoitu."))
        return JsonResponse({'location': self.get_success_url()})
