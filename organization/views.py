# coding=utf-8

from __future__ import unicode_literals
from django.contrib.contenttypes.models import ContentType

from django.core.urlresolvers import reverse
from django.contrib import messages
from django.db import transaction
from django.db.models.query_utils import Q
from django.http.response import JsonResponse, HttpResponseRedirect
from django.utils.translation import ugettext, ugettext_lazy as _
from django.views.generic.base import View

from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView
from django.views.generic.list import ListView

from .models import Organization

from content.models import Idea, Question, Initiative
from nuka.views import PreFetchedObjectMixIn
from organization.forms import CreateOrganizationForm, OrganizationSearchForm, \
    OrganizationSearchFormAdmin
from organization.perms import CanEditOrganization


class OrganizationListView(ListView):
    paginate_by = 20
    model = Organization
    template_name = 'organization/organization_list.html'
    searchform = None
    form_class = None

    def get_form_kwargs(self):
        return {}

    def get_form_class(self):
        if self.request.user.is_authenticated() and self.request.user.is_moderator:
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


class OrganizationDetailView(PreFetchedObjectMixIn, DetailView):
    model = Organization

    def get_context_data(self, **kwargs):
        context = super(OrganizationDetailView, self).get_context_data(**kwargs)

        # If the user can edit the organization, show all their initiatives.
        if CanEditOrganization(request=self.request,
                               obj=self.get_object()).is_authorized():
            context["initiatives_list"] = Initiative.objects.filter(
                Q(initiator_organization=self.get_object()) |
                Q(target_organizations=self.get_object())
            ).order_by("-created").distinct()
        # If the user cannot edit the organization, only show public initiatives.
        else:
            context["initiatives_list"] = Initiative.objects.filter(
                Q(visibility=Initiative.VISIBILITY_PUBLIC),
                Q(initiator_organization=self.get_object()) |
                Q(target_organizations=self.get_object())
            ).order_by("-published").distinct()

        context['ideas_count'] = context['initiatives_list'].exclude(
            polymorphic_ctype_id=ContentType.objects.get_for_model(Question).pk).count()
        context['question_count'] = context['initiatives_list'].exclude(
            polymorphic_ctype_id=ContentType.objects.get_for_model(Idea).pk).count()
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


class OrganizationSetActiveMixIn(PreFetchedObjectMixIn):
    def get_success_url(self):
        return reverse(
            'organization:detail',
            kwargs={'pk': self.get_object().pk}
        )

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
