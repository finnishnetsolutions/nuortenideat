# coding=utf-8

from __future__ import unicode_literals

from django import forms
from django.conf import settings
from django.db.models.aggregates import Sum, Count
from django.db.models import Q
from django.forms.models import ModelForm
from django.forms.widgets import RadioSelect, TextInput
from django.utils import timezone
from django.utils.translation import ugettext, ugettext_lazy as _, string_concat

from nocaptcha_recaptcha import NoReCaptchaField

from libs.attachtor.forms.fields import RedactorAttachtorField
from libs.attachtor.forms.forms import RedactorAttachtorFormMixIn, FileUploadForm
from libs.attachtor.models.models import Upload
from libs.fimunicipality.models import Municipality

from account.models import User
from nkcomments.models import CustomComment
from nuka.forms.forms import HiddenLabelMixIn
from nuka.forms.fields import ModelMultipleChoiceField, SaferFileField
from nuka.forms.widgets import Select2Multiple, AutoSubmitButtonSelect
from nuka.utils import send_email
from organization.models import Organization
from tagging.models import Tag

from .models import Idea, AdditionalDetail, Question, Initiative


class CreateIdeaForm(forms.ModelForm):
    TARGET_TYPE_ORGANIZATION = -1
    TARGET_TYPE_NATION = Organization.TYPE_NATION
    TARGET_TYPE_UNKNOWN = Organization.TYPE_UNKNOWN

    WRITE_AS_USER = 0
    WRITE_AS_ORGANIZATION = 1

    write_as = forms.ChoiceField(
        label=_("Kirjoitetaanko idea organisaationa vai käyttäjänä?"),
        widget=RadioSelect,
        choices=(
            (WRITE_AS_USER,          _("Kirjoita käyttäjänä")),
            (WRITE_AS_ORGANIZATION,  _("Kirjoita organisaationa"))
        ),
        initial=WRITE_AS_USER,
        help_text=_(
            "Olet yhteyshenkilönä vähintään yhdessä organisaatiossa, joten "
            "voit valita kirjoittaa idean organisaationa tai tavallisena käyttäjänä."
        )
    )

    owners = ModelMultipleChoiceField(
        queryset=User.objects.filter(is_active=True),
        label=_("Valitse idean omistajat"),
        help_text=_("Valitse idean muiden omistajien Nuortenideat.fi käyttäjätunnukset.")
    )

    target_type = forms.ChoiceField(
        label=_("Mitä organisaatioita idea koskee?"), widget=RadioSelect,
        initial=TARGET_TYPE_ORGANIZATION,
        choices=(
            (TARGET_TYPE_ORGANIZATION,  _("Valittuja organisaatioita")),
            (TARGET_TYPE_NATION,        _("Idea koskee koko Suomea")),
            (TARGET_TYPE_UNKNOWN,       _("En osaa sanoa")),
        )
    )
    target_organizations = ModelMultipleChoiceField(
        queryset=Organization.objects.real().active(),
        help_text=_("Valitse organisaatio tai organisaatiot, joihin idea liittyy."),
        label='', required=False
    )
    tags = ModelMultipleChoiceField(label=_("Valitse aiheet"), widget=Select2Multiple,
                                    queryset=Tag.objects.all(), required=False)

    def __init__(self, user, *args, **kwargs):
        super(CreateIdeaForm, self).__init__(*args, **kwargs)

        if self.data.get('target_type', None) == self.TARGET_TYPE_ORGANIZATION:
            self.fields['target_organizations'].required = True

        user_organizations = user.organizations.all().active()
        if user_organizations:
            self.fields["initiator_organization"] = forms.ModelChoiceField(
                label=_("Organisaatio, jona idea kirjoitetaan."),
                queryset=user_organizations,
                empty_label=None,
                required=False
            )
        else:
            del self.fields["write_as"]
            del self.fields["initiator_organization"]

    def clean_owners(self):
        """The view should supply initial owners list containing the request.user,
        make sure s/he is still on the list."""
        owners = self.cleaned_data['owners']
        if self.initial['owners'][0] not in owners:
            raise forms.ValidationError(_("Et voi poistaa itseäsi idean omistajista."))
        return owners

    def clean(self):
        cleaned = super(CreateIdeaForm, self).clean()

        if 'target_type' in cleaned:
            target_type = int(cleaned['target_type'])
            if target_type in (self.TARGET_TYPE_UNKNOWN, self.TARGET_TYPE_NATION):
                cleaned['target_organizations'] = [Organization.objects.get(
                    type=target_type
                )]
            elif not cleaned["target_organizations"]:
                self.add_error("target_organizations", _("Tämä kenttä vaaditaan."))

        try:
            if int(cleaned["write_as"]) == self.WRITE_AS_ORGANIZATION:
                cleaned["owners"] = []
            elif int(cleaned["write_as"]) == self.WRITE_AS_USER:
                cleaned["initiator_organization"] = None
        except KeyError:
            pass

        return cleaned

    class Meta:
        model = Idea
        fields = ('title', 'write_as', 'initiator_organization', 'owners', 'target_type',
                  'target_organizations', 'tags', 'interaction')
        widgets = {'interaction': RadioSelect, }


class EditIdeaBaseForm(HiddenLabelMixIn, ModelForm):
    pass


class EditInitiativeTitleForm(EditIdeaBaseForm):
    class Meta:
        model = Initiative
        fields = ('title', )


class EditInitiativeDescriptionForm(RedactorAttachtorFormMixIn, EditIdeaBaseForm):
    class Meta:
        model = Initiative
        fields = ('description', )


class EditIdeaOwnersForm(EditIdeaBaseForm):
    # TODO: Ask confirmation if all owners are to be removed.
    owners = ModelMultipleChoiceField(
        queryset=User.objects.filter(is_active=True),
        label=_("Idean omistajat"),
        help_text=_("Syötä idean omistajien Nuortenideat.fi käyttäjätunnukset"),
        required=False
    )

    def __init__(self, *args, **kwargs):
        self.idea = kwargs["instance"]
        kwargs.setdefault("initial", {})
        kwargs["initial"]["owners"] = self.idea.owners.all()
        super(EditIdeaOwnersForm, self).__init__(*args, **kwargs)

    def send_email_notification(self):
        receivers = set(self.initial["owners"]) | set(self.cleaned_data["owners"])
        for receiver in receivers:
            send_email(
                _("Idean omistajia muutettu."),
                "content/email/owner_change.txt",
                {"idea": self.idea},
                [receiver.settings.email],
                receiver.settings.language
            )

    def save(self, commit=True):
        changed = self.has_changed and "owners" in self.changed_data
        obj = super(EditIdeaOwnersForm, self).save(commit=commit)
        if changed and self.cleaned_data["owners"]:
            self.send_email_notification()
        return obj

    class Meta:
        model = Idea
        fields = ('owners', )


class EditInitiativeTagsForm(EditIdeaBaseForm):
    tags = ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        label=_("Aiheet")
    )

    class Meta:
        model = Initiative
        fields = ('tags', )


class EditIdeaOrganizationsForm(EditIdeaBaseForm):
    target_organizations = ModelMultipleChoiceField(
        queryset=Organization.objects.active(),
        label=_("Organisaatiot")
    )

    class Meta:
        model = Idea
        fields = ('target_organizations', )


class EditIdeaPictureForm(ModelForm):
    picture = forms.ImageField(label=_("Uusi kuva"), widget=forms.FileInput,
                               required=False)

    picture_alt_text = forms.CharField(label=_("Kuvan tekstimuotoinen kuvaus"),
                                       required=False)

    class Meta:
        model = Idea
        fields = ('picture', 'picture_alt_text')


class AdditionalDetailForm(RedactorAttachtorFormMixIn, ModelForm):

    # Redactor-field needs a unique id to work, when using multiple forms on same page
    def __init__(self, *args, **kwargs):
        if 'instance' in kwargs and kwargs['instance'].pk is not None:
            kwargs['prefix'] = 'pre-{}'.format(kwargs['instance'].pk)
        super(AdditionalDetailForm, self).__init__(*args, **kwargs)

    class Meta:
        model = AdditionalDetail
        fields = ('detail',)


class CreateQuestionBaseForm(forms.ModelForm):

    tags = ModelMultipleChoiceField(label=_("Aiheet"), widget=Select2Multiple,
                                    queryset=Tag.objects.all(), required=False)


class CreateQuestionForm(RedactorAttachtorFormMixIn, CreateQuestionBaseForm):
    title = forms.CharField(max_length=255, label=_("Otsikko"))
    description = RedactorAttachtorField(label=_("Viesti"))

    class Meta:
        model = Question
        fields = ('title', 'description', 'tags')
        required = ('description', )


class CreateQuestionFormAnon(CreateQuestionBaseForm):

    user_name = forms.CharField(label=_('Lähettäjän nimi'))
    captcha = NoReCaptchaField(
        label=_('Tarkistuskoodi'),
        error_messages={'invalid': _('Virheellinen tarkistuskoodi.')}
    )
    description = forms.CharField(label=_('Viesti'), widget=forms.Textarea)

    class Meta:
        model = Question
        fields = ('title', 'description', 'tags', 'user_name')


class IdeaToPdfBaseForm(forms.ModelForm):
    included_comments = ModelMultipleChoiceField(queryset=CustomComment.objects.none(),
                                                 label='',
                                                 required=False)

    name = forms.CharField(label=_("Idean omistaja"), required=False)
    contacts = forms.CharField(label=_("Yhteystiedot"), required=False)

    OUTPUT_METHOD_PRINT = 'print'
    OUTPUT_METHOD_EMAIL = 'email'
    OUTPUT_METHODS = (
        (OUTPUT_METHOD_EMAIL, _("Lähetä sähköpostin liitteenä")),
        (OUTPUT_METHOD_PRINT, _("Vie idea eteenpäin muulla tavalla"))
    )

    output_method = forms.ChoiceField(
        label="", widget=forms.RadioSelect,
        choices=OUTPUT_METHODS, initial=OUTPUT_METHODS[0][0], required=False
    )

    EMAIL_RECEIVER_TYPE_INTERNAL = 'internal'
    EMAIL_RECEIVER_TYPE_EXTERNAL = 'external'
    EMAIL_RECEIVER_TYPES = (
        (EMAIL_RECEIVER_TYPE_INTERNAL, _("Valitse Nuortenideat.fi-palvelussa oleva "
                                         "organisaatio vastaanottajaksi")),
        (EMAIL_RECEIVER_TYPE_EXTERNAL, _("... tai organisaatio, joka ei ole palvelussa mukana"))
    )

    email_receiver_type = forms.ChoiceField(
        label="", widget=forms.RadioSelect(attrs={'class': 'email-field'}),
        choices=EMAIL_RECEIVER_TYPES, initial=EMAIL_RECEIVER_TYPES[0][0], required=False
    )

    email_recipient_organization = ModelMultipleChoiceField(
        label=string_concat(_("Valitse vastaanottaja"), '. ',
                            _("Tämä tieto näkyy ideasivulla muille käyttäjille.")),
        widget=Select2Multiple(attrs={'class': 'email-field'}),
        required=False,
        queryset=Organization.objects.normal().filter(admins__isnull=False).distinct()
    )

    email_recipient_name = forms.CharField(
        label=string_concat(_("Vastaanottajan nimi"), '. ',
                            _("Tämä tieto näkyy ideasivulla muille käyttäjille.")),
        required=False,
        widget=TextInput(attrs={'class': 'email-field'}),
        error_messages={'invalid': _("Virheellinen sähköpostiosoite")}
    )

    email_recipient = forms.EmailField(
        label=_("Vastaanottajan sähköpostiosoite"),
        required=False,
        widget=TextInput(attrs={'class': 'email-field'}),
        error_messages={'invalid': _("Virheellinen sähköpostiosoite")}
    )

    email_copy = forms.BooleanField(
        label=_('Lähetä kopio omaan sähköpostiin'),
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'email-field'})
    )

    email_message = forms.CharField(
        label=_("Sähköpostiviesti"),
        widget=forms.Textarea(attrs={'class': 'email-field'}),
        required=False)

    def __init__(self, *args, **kwargs):
        super(IdeaToPdfBaseForm, self).__init__(*args, **kwargs)
        self.fields['included_comments'].queryset = kwargs['instance'].comments.all()
        first_owner = kwargs['instance'].owners.first()
        if first_owner is not None:
            self.fields['name'].initial = first_owner.get_full_name()
            self.fields['contacts'].initial = first_owner.get_contact_information()

    def clean(self):
        cleaned_data = super(IdeaToPdfBaseForm, self).clean()

        output_method = cleaned_data.get('output_method')

        if output_method == self.OUTPUT_METHOD_EMAIL:
            email_receiver_type = cleaned_data.get('email_receiver_type')

            if email_receiver_type == self.EMAIL_RECEIVER_TYPE_INTERNAL:
                del cleaned_data['email_recipient']
                del cleaned_data['email_recipient_name']
                recipient = cleaned_data.get('email_recipient_organization')
                if not recipient:
                    msg = _("Virhe. Vastaanottaja on pakollinen tieto.")
                    self.add_error('email_recipient_organization', msg)
            elif email_receiver_type == self.EMAIL_RECEIVER_TYPE_EXTERNAL:
                del cleaned_data['email_recipient_organization']
                del cleaned_data['additional_detail']
                recipient = cleaned_data.get('email_recipient')
                recipient_name = cleaned_data.get('email_recipient_name')
                if not recipient:
                    msg = _("Virhe. Sähköpostin vastaanottaja on pakollinen tieto.")
                    self.add_error('email_recipient', msg)
                if not recipient_name:
                    msg = _("Virhe. Sähköpostin vastaanottajan nimi on pakollinen tieto.")
                    self.add_error('email_recipient_name', msg)

            if self.errors:
                raise forms.ValidationError(_("Virhe. Sähköpostin vastaanottajan tiedot "
                                              "ovat puutteelliset."))

        return cleaned_data

    class Meta:
        model = Idea
        fields = ()


class IdeaToPdfFormModifier(RedactorAttachtorFormMixIn, IdeaToPdfBaseForm):

    additional_detail = forms.CharField(
        label=string_concat(_("Kirjoita alla olevaan kenttään kenelle ja miten idea on "
                              "viety eteenpäin"), ". ",
                              _("Tämä tieto näkyy ideasivulla muille käyttäjille.")),
        widget=forms.Textarea,
        required=False
    )

    def __init__(self, *args, **kwargs):
        super(IdeaToPdfFormModifier, self).__init__(*args, **kwargs)
        if kwargs['instance'].status != Idea.STATUS_PUBLISHED:
            del self.fields['additional_detail']


class IdeaToPdfForm(IdeaToPdfBaseForm):
    pass


class InitiativeSearchForm(forms.ModelForm):
    organizations = ModelMultipleChoiceField(
        queryset=Organization.objects.active(),
        label=_("Valitse organisaatio"),
        required=False
    )

    tags = ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        label=_("Valitse aihe"),
        required=False
    )

    municipalities = ModelMultipleChoiceField(
        queryset=Municipality.objects.natural().active(),
        label=_("Valitse kunta"),
        required=False
    )

    def filtrate(self, idea_qs):
        organizations = self.cleaned_data['organizations']
        tags = self.cleaned_data['tags']
        municipalities = self.cleaned_data["municipalities"]

        if organizations:
            idea_qs = idea_qs.filter(
                Q(target_organizations__in=organizations) |
                Q(initiator_organization__in=organizations)
            )
        if tags:
            idea_qs = idea_qs.filter(
                tags__in=tags
            )
        if municipalities:
            idea_qs = idea_qs.filter(
                target_organizations__municipalities__in=municipalities
            )

        return idea_qs

    def save(self, commit=True):
        raise Exception("Ei sallittu")


class IdeaSearchForm(InitiativeSearchForm):

    FIELD_STATUS = 'status'
    FIELD_VISIBILITY = 'visibility'

    SEARCH_STATUS_CHOICES = (
        (Idea.STATUS_PUBLISHED,      _("Avoin")),
        (Idea.STATUS_TRANSFERRED,    _("Viety eteenpäin")),
        (Idea.STATUS_DECISION_GIVEN, _("Päätös annettu")),
        (Idea.VISIBILITY_ARCHIVED,   _("Arkistoitu"))
    )

    STATUS_FIELD_MAP = {
        Idea.STATUS_PUBLISHED: 'status',
        Idea.STATUS_TRANSFERRED: 'status',
        Idea.STATUS_DECISION_GIVEN: 'status',
        Idea.VISIBILITY_ARCHIVED: 'visibility',
    }

    status = forms.ChoiceField(choices=(('', _("Kaikki")), ) + SEARCH_STATUS_CHOICES,
                               widget=AutoSubmitButtonSelect, required=False, label=False)

    words = forms.CharField(label=_("Hae ideaa"), required=False)

    organization_initiated = forms.BooleanField(
        label=_('Vain organisaatioiden luomat ideat'),
        required=False
    )

    user = None
    is_authenticated = False

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.is_authenticated = self.user.is_authenticated() if \
            hasattr(self.user, 'is_authenticated') else False

        super(IdeaSearchForm, self).__init__(*args, **kwargs)

        # Set the result count to the status labels.
        new_choices = []
        for status, label in self.fields['status'].choices:
            if status:
                status_field = self.STATUS_FIELD_MAP[int(status)]
                queryset = Idea._default_manager.filter(**{status_field: status})

                if status_field != self.FIELD_VISIBILITY:
                    queryset = queryset.filter(visibility=Initiative.VISIBILITY_PUBLIC)
                else:
                    if status == Idea.VISIBILITY_ARCHIVED:
                        # remove option "archived" if not authenticated
                        if not self.is_authenticated:
                            continue
                        queryset = self.filter_visibility_archived_qs(queryset)
            else:
                queryset = Idea.objects.exclude(visibility=Idea.VISIBILITY_ARCHIVED)

            label = "{} ({})".format(label, queryset.count())
            new_choices.append((status, label))

        self.fields['status'].choices = new_choices

    def filter_visibility_archived_qs(self, qs):
        if not self.is_authenticated:
            return qs.none()

        # if not moderator, then only show archived ideas owned by user
        if not self.user.is_moderator:
            options = {'owners': self.user}

            # for organization admins even targeted ideas
            if self.user.organization_ids:
                qs = qs.filter(
                    Q(**options) |
                    Q(initiator_organization__in=self.user.organization_ids) |
                    Q(target_organizations__in=self.user.organization_ids))
            else:
                qs = qs.filter(**options)
        return qs

    def filtrate(self, idea_qs):
        idea_qs = super(IdeaSearchForm, self).filtrate(idea_qs)

        status = self.cleaned_data['status']
        words = self.cleaned_data['words']
        organization_initiated = self.cleaned_data["organization_initiated"]
        if status:
            status_field = self.STATUS_FIELD_MAP[int(status)]
            idea_qs = idea_qs.filter(**{status_field: status})

            if status_field == self.FIELD_VISIBILITY \
                    and int(status) == Idea.VISIBILITY_ARCHIVED:
                idea_qs = self.filter_visibility_archived_qs(idea_qs)

        if words:
            idea_qs = idea_qs.filter(search_text__icontains=words)

        if not status or not self.FIELD_VISIBILITY == status_field:
            idea_qs = idea_qs.filter(visibility=Initiative.VISIBILITY_PUBLIC)

        if organization_initiated:
            idea_qs = idea_qs.exclude(initiator_organization__isnull=True)

        return idea_qs.order_by('-published')

    class Meta:
        model = Idea
        fields = ('organizations', 'tags')


class AttachmentUploadForm(FileUploadForm):
    file = SaferFileField()

    def __init__(self, *args, **kwargs):
        self.uploader = kwargs.pop('uploader')
        self.upload_group = kwargs.pop('upload_group')
        super(FileUploadForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned = super(AttachmentUploadForm, self).clean()
        limits = settings.ATTACHMENTS
        if 'file' in cleaned:
            file = cleaned['file']
            if file.size > limits['max_size']:
                raise forms.ValidationError(ugettext("Tiedosto ylittää kokorajoituksen."))
            if self.upload_group is not None:
                obj_totals = self.upload_group.upload_set.aggregate(
                    count=Count('id'), total_size=Sum('size')
                )
                if (obj_totals['count'] or 0) >= limits['max_attachments_per_object']:
                    raise forms.ValidationError(
                        ugettext("Liian monta liitetiedostoa lisätty.")
                    )
            uploader_total = Upload.objects.filter(
                uploader=self.uploader,
                created__gte=timezone.now()-limits['max_size_per_uploader_timeframe']
            ).aggregate(size=Sum('size'))
            if (uploader_total['size'] or 0) + file.size > \
                    limits['max_size_per_uploader']:
                raise forms.ValidationError(
                    ugettext("Olet lisännyt liian monta liitetiedostoa. "
                             "Yritä myöhemmin uudestaan.")
                )
        return cleaned


class PublishIdeaDecisionForm(forms.Form):
    # TODO: RedactorAttachtorField
    additional_detail = forms.CharField(label=_("Lisätieto"), widget=forms.Textarea,
                                        required=False)


class KuaTransferBlankForm(forms.ModelForm):
    def save(self, commit=True):
        raise Exception("i don't want to be saved")

    class Meta:
        model = Idea
        fields = ()


class KuaTransferMembershipReasonForm(KuaTransferBlankForm):
    MEMBERSHIP_COMMUNITY = 'community'
    MEMBERSHIP_COMPANY = 'company'
    MEMBERSHIP_PROPERTY = 'property'
    MEMBERSHIP_NONE = 'none'

    MEMBERSHIP_CHOICES = (
        (MEMBERSHIP_COMMUNITY,  _("Nimenkirjoitusoikeus yhteisössä, laitoksessa tai "
                                  "säätiössä, jonka kotipaikka on aloitetta koskevassa "
                                  "kunnassa")),
        (MEMBERSHIP_COMPANY,    _("Nimenkirjoitusoikeus yrityksessä, jonka kotipaikka on "
                                  "aloitetta koskevassa kunnassa")),
        (MEMBERSHIP_PROPERTY,   _("Hallinta-oikeus tai omistus kiinteään omaisuuteen "
                                  "aloitetta koskevassa kunnassa")),
        (MEMBERSHIP_NONE,       _("Ei mitään näistä")),
    )
    membership = forms.ChoiceField(choices=MEMBERSHIP_CHOICES, widget=RadioSelect,
                                   label=_("Onko sinulla jokin seuraavista?"))

    def clean_membership(self):
        value = self.cleaned_data['membership']
        if value == self.MEMBERSHIP_NONE:
            raise forms.ValidationError(ugettext("Et voi tehdä kuntalaisaloitetta "
                                                 "kuntaan, jossa et ole jäsenenä."))
        return value

    class Meta:
        model = Idea
        fields = ('membership', )
