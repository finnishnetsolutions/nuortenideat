# coding=utf-8

from __future__ import unicode_literals
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.views import password_change
from django.contrib.contenttypes.models import ContentType

from django.views import generic
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _, ugettext
from django.core.urlresolvers import reverse, reverse_lazy
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages

from libs.djcontrib.views.generic import MultiModelFormView

from account.models import GROUP_NAME_ADMINS, GROUP_NAME_MODERATORS
from account.models import User
from .forms import EditUserForm, EditUserSettingsForm
from libs.moderation.models import ModeratedObject, MODERATION_STATUS_PENDING
from nkadmin.forms import UserSearchForm
from nuka.perms import IsAdmin
from organization.models import Organization

QS_PAGE = "sivu"
QS_ORDER_BY = "jarjestys"
QS_SEARCH = "haku"


class QueryString():
    """ Handles URL query strings. """
    components = {}

    def get_base(self, prefix="?", skip=()):
        if not self.components:
            return ""
        else:
            for_join = []
            for key, value in self.components.items():
                if key in skip:
                    continue

                if type(value) is list:
                    for v in value:
                        for_join.append(key + "=" + v)
                else:
                    for_join.append(key + "=" + value)

            if not for_join:
                return ""
            else:
                return prefix + "&".join(for_join)

    def get(self):
        return self.get_base()

    def set(self, component, value):
        self.components[component] = value


class PagedQueryString(QueryString):
    """ Handles URL query strings with paginations. """
    page = None

    def get(self, prefix="?", skip=()):
        if self.page:
            self.components[QS_PAGE] = str(self.page.number)

        return self.get_base(prefix, skip)

    def get_next_page(self):
        if self.page and self.page.has_next():
            self.components[QS_PAGE] = str(self.page.next_page_number())

        return self.get_base()

    def get_previous_page(self):
        if self.page and self.page.has_previous():
            self.components[QS_PAGE] = str(self.page.previous_page_number())

        return self.get_base()

    def get_without_page(self):
        return self.get_base(prefix="&", skip=(QS_PAGE))

    def get_without_page_dpf(self):
        # DPF = Default Prefix, which means '?'.
        return self.get_base(skip=(QS_PAGE))


class UsersQueryString(PagedQueryString):

    def get_without_order(self):
        return self.get(prefix="&", skip=QS_ORDER_BY)


class UsersView(generic.ListView):
    # TODO: Remake using djangos pagination. Possibly get rid of the querystring class.

    template_name = "nkadmin/users_list.html"
    model = User
    filter = "kaikki"
    order_by = ""
    search = ""
    queryset = None
    users_per_page = 50
    query_string = UsersQueryString()
    form_class = UserSearchForm

    def get_queryset(self):
        self.query_string.components = {}
        try:
            self.filter = self.kwargs['filter']
        except KeyError:
            pass
        if self.request.GET.get(QS_ORDER_BY):
            self.query_string.components[QS_ORDER_BY] = self.request.GET.get(QS_ORDER_BY)
            self.order_by = self.request.GET.get(QS_ORDER_BY)
        if self.request.GET.get(QS_SEARCH):
            self.query_string.components[QS_SEARCH] = self.request.GET.get(QS_SEARCH)
            self.search = self.request.GET.get(QS_SEARCH)

        if 'organizations' in self.request.GET:
            self.query_string.components['organizations'] = \
                self.request.GET.getlist('organizations')

        if not self.queryset:
            self.set_queryset()

        form = self.form_class(self.request.GET)
        if self.request.GET and form.is_valid():
            self.queryset = form.form_filter(self.queryset)

        return self.queryset

    def get_default_queryset(self):
        return User.objects.all()

    def set_queryset(self):
        if self.filter == "yllapitajat":
            qs = User.objects.filter(groups__name=GROUP_NAME_ADMINS)
        elif self.filter == "moderaattorit":
            qs = User.objects.filter(groups__name=GROUP_NAME_MODERATORS)
        #elif self.filter == "osallistujat":
        #    qs = User.objects.exclude(groups__name=GROUP_NAME_ADMINS).exclude(
        #        groups__name=GROUP_NAME_MODERATORS)
        else:
            if self.filter == 'kaikki' or not self.filter:
                qs = self.get_default_queryset()
            else:
                qs = User.objects.exclude(groups__name=GROUP_NAME_ADMINS).exclude(
                    groups__name=GROUP_NAME_MODERATORS)
                if self.filter == 'osallistujat':
                    qs = qs.filter(organizations__isnull=True)
                elif self.filter == 'yhteyshenkilot':
                    qs = qs.filter(organizations__isnull=False)

        if self.search:
            qs = qs.filter(
                Q(settings__first_name__istartswith=self.search) |
                Q(settings__last_name__istartswith=self.search) |
                Q(username__istartswith=self.search) |
                Q(organizations__name__icontains=self.search) |
                Q(settings__municipality__name_fi__istartswith=self.search) |
                Q(settings__municipality__name_sv__istartswith=self.search)
            )

        if self.order_by:
            if self.order_by == "nimi":
                qs = qs.order_by("settings__last_name")
            elif self.order_by == "kotikunta":
                qs = qs.order_by("settings__municipality")
            elif self.order_by == "organisaatio":
                qs = qs.order_by("organizations__name")

        self.queryset = qs.distinct()

    def get_context_data(self, **kwargs):
        context = super(UsersView, self).get_context_data(**kwargs)
        context["active_users"] = True
        context["filter"] = self.filter
        context["order_by"] = self.order_by
        context["last_search"] = self.search

        paginator = Paginator(self.queryset, self.users_per_page)
        if self.request.GET.get(QS_PAGE):
            page = self.request.GET.get(QS_PAGE)
        else:
            page = 1
        try:
            context["users"] = paginator.page(page)
        except PageNotAnInteger:
            context["users"] = paginator.page(1)
        except EmptyPage:
            context["users"] = paginator.page(paginator.num_pages)

        self.query_string.page = context["users"]
        context["query_string"] = self.query_string
        context['form'] = self.form_class(self.request.GET)

        return context


class EditUserView(MultiModelFormView):
    template_name = "nkadmin/edit_user.html"
    form_classes = (
        ("user", EditUserForm),
        ("usersettings", EditUserSettingsForm)
    )
    
    def get_user_form_kwargs(self, kwargs):
        kwargs["target_user"] = self.kwargs["pk"]
        kwargs["editor_is_admin"] = IsAdmin(request=self.request).is_authorized()
        return kwargs

    def get_success_url(self):
        messages.success(self.request, ugettext('Käyttäjän tiedot tallennettu.'))
        return reverse('nkadmin:users_edit', kwargs={"pk": self.kwargs["obj"].pk})

    def get_user_object(self):
        return self.kwargs["obj"]

    def get_usersettings_object(self):
        return self.kwargs["obj"].settings


class SetPasswordView(generic.UpdateView):
    model = User
    form_class = SetPasswordForm
    template_name = "nkadmin/change_user_password.html"
    success_url = reverse_lazy("nkadmin:users")

    def get_form_kwargs(self):
        kwargs = super(SetPasswordView, self).get_form_kwargs()
        kwargs.pop("instance")
        kwargs["user"] = self.object
        return kwargs

    def form_valid(self, form):
        form.save()
        update_session_auth_hash(self.request, form.user)
        msg = _("Käyttäjän %s salasana vaihdettu.") % self.object
        messages.success(self.request, msg)
        return super(SetPasswordView, self).form_valid(form)


class ModerationQueueBaseView(generic.ListView):
    model = ModeratedObject
    template_name = 'nkadmin/moderation_queue.html'
    paginate_by = 40


class ModerationQueueView(ModerationQueueBaseView):
    def get_queryset(self):
        ct = ContentType.objects.get_for_model(Organization)
        return self.model.objects.filter(moderation_status=MODERATION_STATUS_PENDING).\
            exclude(content_type_id=ct.pk).order_by('-date_updated', '-pk')


class ModerationOrganizationQueueView(ModerationQueueBaseView):
    def get_queryset(self):
        ct = ContentType.objects.get_for_model(Organization)
        return self.model.objects.filter(
            moderation_status=MODERATION_STATUS_PENDING,
            content_type_id=ct.pk
        ).order_by('-pk')
