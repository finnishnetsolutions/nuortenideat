# coding=utf-8

from __future__ import unicode_literals

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db.models.query_utils import Q
from django.forms.models import ModelForm
from django.utils.translation import ugettext, ugettext_lazy as _
from content.forms import IdeaSearchForm, IdeaStatusForm
from content.models import Initiative, Idea, Question

from libs.attachtor.forms.forms import RedactorAttachtorFormMixIn
from libs.fimunicipality.models import Municipality

from nuka.forms.fields import ModelMultipleChoiceField
from account.models import User
from nuka.forms.forms import HiddenLabelMixIn
from nuka.forms.widgets import Select2Multiple, AutoSubmitButtonSelect
from nuka.utils import send_email

from .models import Organization


class OrganizationAdminsField(ModelMultipleChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('queryset', User.objects.filter(is_active=True))
        kwargs.setdefault('label', ugettext("Valitse yhteyshenkilöt"))
        kwargs.setdefault('help_text', ugettext("Valitse organisaation yhteyshenkilöiden "
                                                "Nuortenideat.fi käyttäjätunnukset."))
        super(OrganizationAdminsField, self).__init__(*args, **kwargs)


class OrganizationAdminsMixin(object):
    def __init__(self, *args, **kwargs):
        org = kwargs.get('instance', None)
        if org is not None:
            kwargs.setdefault('initial', {})
            kwargs['initial']['admins'] = org.admins.all()
        super(OrganizationAdminsMixin, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        assert commit is True, "Must commit"
        instance = super(OrganizationAdminsMixin, self).save()
        instance.admins = self.cleaned_data['admins']
        instance.save()
        return instance


class CreateOrganizationForm(RedactorAttachtorFormMixIn, OrganizationAdminsMixin,
                             forms.ModelForm):
    # magic types "Nation" / "Unknown" cannot be selected
    type = forms.ChoiceField(choices=[(k, v) for k,v in Organization.TYPE_CHOICES
                                      if k not in Organization.MAGIC_TYPES],
                             label=_("Organisaation tyyppi"))
    admins = OrganizationAdminsField()
    municipalities = ModelMultipleChoiceField(
        label=_("Valitse kunnat"),
        queryset=Municipality.objects.natural().active(),
        widget=Select2Multiple,
        required=False,
        help_text=_("Valitse kunta tai kunnat, joiden alueella organisaatio toimii. "
                    "Jätä tyhjäksi, jos organisaatio on valtakunnallinen.")
    )
    terms_accepted = forms.BooleanField()

    def __init__(self, *args, **kwargs):
        super(CreateOrganizationForm, self).__init__(*args, **kwargs)
        self.fields["terms_accepted"].label = _(
            'Hyväksyn <a href="{}" target="_blank">käyttöehdot</a>.'.format(
                reverse("help:instruction_detail", args=[27])
            )
        )

    def clean_admins(self):
        """The view should supply initial owners list containing the request.user,
        make sure s/he is still on the list."""
        admins = self.cleaned_data['admins']
        if self.initial['admins'][0] not in admins:
            raise forms.ValidationError(_("Et voi poistaa itseäsi yhteyshenkilöistä."))
        return admins

    def clean_municipalities(self):
        v = self.cleaned_data['municipalities']
        org_type = int(self.cleaned_data.get('type', -1))  # it's unicode, why?
        if org_type == Organization.TYPE_MUNICIPALITY and len(v) != 1:
            raise forms.ValidationError("Kunta-tyyppisen organisaation täytyy liittyä "
                                        "täsmälleen yhteen kuntaan.")
        return v

    class Meta:
        model = Organization
        fields = ('type', 'name', 'description', 'municipalities', 'admins',
                  'terms_accepted')


class EditOrganizationBaseForm(HiddenLabelMixIn, ModelForm):
    pass


class EditOrganizationNameForm(EditOrganizationBaseForm):

    class Meta:
        model = Organization
        fields = ('name', )


class EditOrganizationDescriptionForm(RedactorAttachtorFormMixIn,
                                      EditOrganizationBaseForm):

    class Meta:
        model = Organization
        fields = ('description', )


class EditOrganizationTypeForm(EditOrganizationBaseForm):
    type = forms.ChoiceField(
        choices=[(k, v) for k, v in Organization.TYPE_CHOICES
                 if k not in Organization.MAGIC_TYPES],
        label=_("Tyyppi")
    )

    class Meta:
        model = Organization
        fields = ("type", )


class EditOrganizationAdminsForm(OrganizationAdminsMixin, EditOrganizationBaseForm):
    admins = OrganizationAdminsField()

    def __init__(self, *args, **kwargs):
        super(EditOrganizationAdminsForm, self).__init__(*args, **kwargs)
        self.organization = kwargs["instance"]

    def send_email_notification(self):
        receivers = set(self.initial["admins"]) | set(self.cleaned_data["admins"])
        for receiver in receivers:
            send_email(
                _("Organisaation yhteyshenkilöitä on muutettu."),
                "organization/email/owner_change.txt",
                {"organization": self.organization},
                [receiver.settings.email],
                receiver.settings.language
            )

    def save(self, commit=True):
        changed = self.has_changed()
        super(EditOrganizationAdminsForm, self).save(commit)
        if changed:
            self.send_email_notification()

    class Meta:
        model = Organization
        fields = ('admins', )


class EditPictureForm(forms.ModelForm):
    picture = forms.ImageField(label=_("Valitse kuva"), widget=forms.FileInput,
                               required=False)

    class Meta:
        model = Organization
        fields = ('picture', )


class CropPictureForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ('original_picture', 'cropping', )


class OrganizationBaseSearchForm(ModelForm):

    NOT_ACTIVE = 'not active'
    SEARCH_TYPE_CHOICES = (
        (Organization.TYPE_MUNICIPALITY,    _("Kunta")),
        (Organization.TYPE_ORGANIZATION,    _("Järjestö")),
        (Organization.TYPE_SCHOOL,          _("Koulu tai oppilaitos")),
        (Organization.TYPE_OTHER,           _("Muu organisaatio")),
    )

    type_or_activity = forms.ChoiceField(
        choices=(("", _("Kaikki")), ) + SEARCH_TYPE_CHOICES,
        widget=AutoSubmitButtonSelect, required=False, label=False
    )

    words = forms.CharField(
        label=_("Hae organisaatio"), required=False,
        widget=forms.TextInput(attrs={'placeholder': _("Hae organisaatio")})
    )

    municipalities = ModelMultipleChoiceField(
        queryset=Municipality.objects.natural().active(),
        label=_("Valitse kunta"),
        required=False
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(OrganizationBaseSearchForm, self).__init__(*args, **kwargs)

        # Set the result count to the status labels.
        choices = []
        for value, label in self.fields['type_or_activity'].choices:
            if value:
                if value is self.NOT_ACTIVE:
                    qs = Organization._default_manager.filter(is_active=False)
                    if not self.user.is_moderator:
                        qs = qs.filter(pk__in=self.user.organization_ids)
                else:
                    qs = Organization.objects.filter(type=value)
            else:
                if self.NOT_ACTIVE in self.fields['type_or_activity'].choices:
                    qs = Organization.objects.normal_and_inactive()
                else:
                    qs = Organization.objects.real()

            label = "{} ({})".format(label, qs.count())
            choices.append((value, label))

        self.fields['type_or_activity'].choices = choices

    def filtrate(self, qs):
        organization_type = self.cleaned_data["type_or_activity"]
        words = self.cleaned_data["words"]
        municipalities = self.cleaned_data["municipalities"]
        if organization_type:

            if organization_type == self.NOT_ACTIVE:
                qs = qs.filter(is_active=0)
                if not self.user.is_moderator:
                    qs = qs.filter(pk__in=self.user.organization_ids)
            else:
                if int(organization_type) == Organization.TYPE_OTHER:
                    other_types = (
                        Organization.TYPE_OTHER,
                        Organization.TYPE_NATION,
                        Organization.TYPE_UNKNOWN
                    )
                    qs = qs.filter(type__in=other_types)
                else:
                    qs = qs.filter(type=organization_type)
        else:
            qs = qs.filter(is_active=1)

        if words:
            qs = qs.filter(search_text__icontains=words)

        if municipalities:
            qs = qs.filter(
                municipalities__in=municipalities
            )

        return qs.order_by("-created")

    def save(self, commit=True):
        raise Exception("Ei sallittu.")

    class Meta:
        model = Organization
        fields = ('type_or_activity',)


class OrganizationSearchForm(OrganizationBaseSearchForm):
    pass


class OrganizationSearchFormAdmin(OrganizationBaseSearchForm):
    ADMIN_CHOICES = OrganizationBaseSearchForm.SEARCH_TYPE_CHOICES + \
              ((OrganizationBaseSearchForm.NOT_ACTIVE, _("Arkistoitu/piilotettu")), )
    type_or_activity = forms.ChoiceField(
        choices=(("", _("Kaikki")), ) + ADMIN_CHOICES,
        widget=AutoSubmitButtonSelect, required=False, label=False
    )


class OrganizationDetailIdeaListForm(IdeaStatusForm):

    TYPE_CHOICES = [
        ('', _("Kaikki")),
        (ContentType.objects.get_for_model(Idea).id, _("Ideat")),
        (ContentType.objects.get_for_model(Question).id, _("Kysymykset")),
    ]

    initiative_ct_id = forms.ChoiceField(choices=TYPE_CHOICES,
                                         widget=AutoSubmitButtonSelect, required=False,
                                         label=_("Näytä"))

    user = None
    is_authenticated = False

    def __init__(self, *args, **kwargs):
        self.is_admin = kwargs.pop('is_admin', None)
        super(OrganizationDetailIdeaListForm, self).__init__(*args, **kwargs)

        new_choices = []
        for status, label in self.fields['status'].choices:
            if status:
                status_field = self.STATUS_FIELD_MAP[int(status)]
                if status_field == self.FIELD_VISIBILITY:
                    if status == Idea.VISIBILITY_ARCHIVED:
                        # remove option "archived" if not authenticated
                        if not self.is_admin:
                            continue
            new_choices.append((status, label))
        self.fields['status'].choices = new_choices

    def filter(self, qs):
        ct_id = self.cleaned_data.get('initiative_ct_id', None)
        qs = self.filter_status(qs, publicity_filter=False)
        if ct_id:
            qs = qs.filter(polymorphic_ctype_id=ct_id)
        return qs

    def filter_visibility_archived_qs(self, qs):
        if not self.is_admin:
            return qs.none()
        return qs.filter(visibility=Initiative.VISIBILITY_ARCHIVED)

    class Meta:
        model = Initiative
        fields = ('initiative_ct_id', 'status', )


