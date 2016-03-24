# coding=utf-8

from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from libs.multilingo.models.fields import MultilingualTextField
from content.models import Initiative

@python_2_unicode_compatible
class Tag(models.Model):
    name = MultilingualTextField(_("nimi"), max_length=50)

    def __str__(self):
        return '#%s' % self.name

    @property
    def popularity(self):
        return Initiative.objects.filter(tags=self).count()

    class Meta:
        verbose_name = _("Aihe")
        verbose_name_plural = _("Aiheet")
