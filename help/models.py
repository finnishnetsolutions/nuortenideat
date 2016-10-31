# coding=utf-8

from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey

from libs.multilingo.models.fields import MultilingualTextField
from slug.models import SlugifiedModel


@python_2_unicode_compatible
class Instruction(MPTTModel, SlugifiedModel):
    title = MultilingualTextField(_("Otsikko"), max_length=255)
    description = MultilingualTextField(_("Sisältö"))
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children',
                            db_index=True)

    TYPE_PRIVACY_POLICY = 'privacy-policy'
    TYPE_CONTACT_DETAILS = 'contact-details'
    TYPES = (
        (None, _("ei mitään")),
        (TYPE_PRIVACY_POLICY, _("rekisteriseloste")),
        (TYPE_CONTACT_DETAILS, _("yhteystiedot")),
    )
    TYPE_CHOICES = list(TYPES)
    connect_link_type = models.CharField(choices=TYPE_CHOICES, default=None, null=True,
                                         unique=True, max_length=50, blank=True)

    def __str__(self):
        return '%s' % self.title

    # inherits SlugifiedModel get_absolute_url
    def absolute_url_viewname(self):
        return 'help:instruction_detail'

    def slugifiable_text(self):
        return self.title

    class MPTTMeta:
        order_insertion_by = ['title']

    class Meta:
        verbose_name = _("ohje")
        verbose_name_plural = _("ohjeet")
