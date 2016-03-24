# coding=utf-8

from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _, get_language, ugettext


@python_2_unicode_compatible
class ParticipatingMunicipality(models.Model):
    """Frequently updated cache of municipalities that are currently participating in KUA
    (kuntalaisaloite.fi")."""
    municipality = models.OneToOneField('fimunicipality.Municipality',
                                        related_name='kua_participation')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.municipality.long_name


@python_2_unicode_compatible
class KuaInitiative(models.Model):
    kua_id = models.IntegerField(primary_key=True)
    idea = models.OneToOneField('content.Idea', related_name='kua_initiative',
                                on_delete=models.CASCADE)
    created_by = models.ForeignKey('account.User')
    management_url = models.CharField(max_length=255)

    def get_absolute_url(self):
        return settings.KUA_API['initiative_urls'][get_language()] % {
            'initiative_id': self.kua_id
        }

    def is_editable(self):
        return self.statuses.count() <= 1  # first status is 'draft'

    def is_public(self):
        return not self.is_editable()

    def __str__(self):
        return "KuaInitiative(kua_id=%d, idea_id=%d)" % (self.kua_id, self.idea_id)


class KuaInitiativeStatus(models.Model):
    STATUS_DRAFT = 'draft'          # initial state, inserted by NUA when the initiative
                                    # is first exported to KUA

    STATUS_PUBLISHED = 'published'  # initiative has been published @ KUA
    STATUS_SENT_TO_MUNICIPALITY = 'sent-to-municipality'
    STATUS_DECISION_GIVEN = 'decision-given'

    STATUS_CHOICES = (
        (STATUS_DRAFT,                  _("Luonnos")),
        (STATUS_PUBLISHED,              _("Julkaistu")),
        (STATUS_SENT_TO_MUNICIPALITY,   _("Lähetetty kuntaan")),
        (STATUS_DECISION_GIVEN,         _("Päätös annettu")),
    )

    kua_initiative = models.ForeignKey(KuaInitiative, related_name='statuses',
                                       on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    created = models.DateTimeField(default=timezone.now)

    def get_friendly_status_message(self):
        if self.status in (self.STATUS_PUBLISHED, self.STATUS_SENT_TO_MUNICIPALITY):
            return mark_safe('<a href="%s">%s</a>' % (
                escape(self.kua_initiative.get_absolute_url()),
                escape(ugettext("Muunnettu aloitteeksi"))
            ))
        return None

    class Meta:
        ordering = ('-pk', )
        verbose_name_plural = "Kua statuses"
        unique_together = (('kua_initiative', 'status'),)
