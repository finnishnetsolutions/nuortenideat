# coding=utf-8
from __future__ import unicode_literals

import bleach
from django.core.urlresolvers import reverse

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from libs.multilingo.models.fields import MultilingualTextField

@python_2_unicode_compatible
class Topic(models.Model):
    title = MultilingualTextField(_("Otsikko"), max_length=255)
    description = MultilingualTextField(_("Sisältö"))
    date = models.DateTimeField(null=True, default=None, blank=True)

    def __str__(self):
        return "{0} {1}".format(
            self.date,
            self.title
        )

    def get_absolute_url(self):
        return reverse('info:topic_detail', kwargs={'pk': self.pk})

    def description_plaintext(self):
        desc = '%s' % self.description
        return bleach.clean(desc.replace('>', '> '),
                            tags=[], strip=True, strip_comments=True).strip()

    class Meta:
        verbose_name = _("Ajankohtaista")
        verbose_name_plural = _("Ajankohtaiset")
        ordering = ['-date']