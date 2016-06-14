# coding=utf-8

from __future__ import unicode_literals

import bleach
from uuid import uuid4

from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch.dispatcher import receiver
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from image_cropping.fields import ImageRatioField

from imagekit.models.fields import ProcessedImageField, ImageSpecField
from pilkit.processors.resize import ResizeToFit, SmartResize
from account.models import User, GROUP_NAME_MODERATORS
from actions.models import ActionGeneratingModelMixin
from cropping.fields import ProcessedImageFieldWithCropping
from cropping.models import CroppingModelMixin

from libs.moderation.models import MODERATION_STATUS_APPROVED
from libs.moderation.signals import post_moderation

from kuaapi.models import ParticipatingMunicipality

from nuka.models import MultilingualRedactorField, MultilingualTextField
from nuka.utils import strip_tags


def _organization_pic_path(obj, name):
    return 'organization/%d/pictures/%s.jpg' % (obj.pk, uuid4().hex)


class OrganizationQuerySet(models.QuerySet):
    def real(self):
        return self.filter(type__gt=max(self.model.MAGIC_TYPES))

    def active(self):
        return self.filter(is_active=True)

    def normal(self):
        return self.filter(type__gt=self.model.TYPE_UNKNOWN).active()

    def normal_and_inactive(self):
        return self.filter(type__gt=self.model.TYPE_UNKNOWN)


@python_2_unicode_compatible
class Organization(ActionGeneratingModelMixin, models.Model, CroppingModelMixin):
    TYPE_UNKNOWN = 0
    TYPE_NATION = 1
    TYPE_ORGANIZATION = 3
    TYPE_MUNICIPALITY = 4
    TYPE_SCHOOL = 5
    TYPE_OTHER = 10
    TYPE_CHOICES = (
        (TYPE_UNKNOWN,      _("Tuntematon")),
        (TYPE_NATION,       _("Koko Suomi")),
        (TYPE_ORGANIZATION, _("Järjestö")),
        (TYPE_MUNICIPALITY, _("Kunta")),
        (TYPE_SCHOOL,       _("Koulu tai muu oppilaitos")),
        (TYPE_OTHER,        _("Muu organisaatio")),
    )
    # these can't be selected for new organizations:
    MAGIC_TYPES = (TYPE_UNKNOWN, TYPE_NATION)

    type = models.SmallIntegerField(_("tyyppi"), choices=TYPE_CHOICES)
    name = MultilingualTextField(_("nimi"), max_length=255, simultaneous_edit=True)
    description = MultilingualRedactorField(_("kuvaus"), blank=True)
    municipalities = models.ManyToManyField(
        'fimunicipality.Municipality',
        related_name=_("Kunnat"),
        verbose_name=_("Valitse kunnat, joiden alueella organisaatio toimii.")
    )

    # cropping
    original_picture = ProcessedImageFieldWithCropping(
        upload_to=_organization_pic_path,
        processors=[ResizeToFit(width=1280, height=1280, upscale=False)],
        format='JPEG', options={'quality': 90}, default=""
    )

    picture = ProcessedImageField(
        upload_to=_organization_pic_path, max_length=120,
        processors=[ResizeToFit(width=1280, height=1280, upscale=False)],
        format='JPEG', options={'quality': 90},
        null=True, default=None, blank=True
    )
    picture_medium = ImageSpecField(source='picture',
                                    processors=[SmartResize(width=220, height=220)],
                                    format='JPEG', options={'quality': 70})
    cropping = ImageRatioField('original_picture', '220x220', size_warning=True,
                               verbose_name=_("Profiilikuvan rajaus"))
    is_active = models.BooleanField(_("aktiivinen"), default=False)
    created = models.DateTimeField(_("luotu"), default=timezone.now)

    # TODO: validation: municipality must be unique if type == TYPE_MUNICIPALITY

    search_text = models.TextField(null=True, default=None)

    objects = OrganizationQuerySet.as_manager()

    def __str__(self):
        return '%s' % self.name

    def get_cropping_cancel_url(self):
        return reverse('organization:picture', kwargs={'pk': self.pk})

    def get_absolute_url(self):
        return reverse('organization:detail', kwargs={'pk': self.pk})

    def is_real_organization(self):
        return self.type not in self.MAGIC_TYPES

    def participates_in_kua(self):
        if self.type != self.TYPE_MUNICIPALITY:
            return False
        try:
            return bool(self.municipalities.first().kua_participation.pk)
        except ParticipatingMunicipality.DoesNotExist:
            return False

    def description_plaintext(self):
        desc = '%s' % self.description
        return bleach.clean(desc.replace('>', '> '),
                            tags=[], strip=True, strip_comments=True).strip()

    def admins_str(self):
        admin_list = [a.get_full_name() for a in self.admins.all()]
        return ", ".join(admin_list)

    # action processing
    def action_kwargs_on_create(self):

        return {'actor': None}

    def fill_notification_recipients(self, action):
        for u in User.objects.filter(groups__name=GROUP_NAME_MODERATORS):
            action.add_notification_recipients(action.ROLE_MODERATOR, u)

    class Meta:
        verbose_name = _("organisaatio")
        verbose_name_plural = _("organisaatiot")


@receiver(signal=post_moderation, sender=Organization)
def activate_approved_organization(instance=None, status=None, **kwargs):
    if status == MODERATION_STATUS_APPROVED and not instance.is_active:
        instance.is_active = True
        instance.save()

@receiver(pre_save, sender=Organization)
def update_search_text(instance=None, **kwargs):
    instance.search_text = ' '.join(map(strip_tags, instance.name.values() +
                                        instance.description.values()))
