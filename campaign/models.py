# coding=utf-8

from __future__ import unicode_literals

from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

from nuka.models import MultilingualTextField


@python_2_unicode_compatible
class Campaign(MPTTModel):
    title = MultilingualTextField(_("Otsikko"), max_length=255)
    description = MultilingualTextField(_("Sisältö"))
    parent = TreeForeignKey("self", null=True, blank=True, related_name="children",
                            db_index=True)

    def __str__(self):
        return "{}".format(self.title)

    class MPTTMeta:
        order_insertion_by = ["title"]

    class Meta:
        verbose_name = _("Kampanja")
        verbose_name_plural = _("Kampanjat")
