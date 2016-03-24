# coding=utf-8

from __future__ import unicode_literals

from django import forms
from django.utils.translation import ugettext_lazy as _
from account.models import UserSettings

from content.forms import IdeaSearchForm


class WidgetIdeaForm(IdeaSearchForm):
    DEFAULT_COLOR = "magenta"
    COLOR_CHOICES = (
        ("magenta", _("Purppura")),
        ("green", _("Vihreä")),
        ("blue", _("Sininen")),
        ("grey", _("Harmaa")),
        ("white", _("Valkoinen"))
    )
    color = forms.ChoiceField(label=_("Väri"), choices=COLOR_CHOICES, required=False)

    DEFAULT_LIMIT = 5
    LIMIT_CHOICES = [(k, k) for k in (3, 4, 5, 6, 7, 8, 9, 10)]
    limit = forms.ChoiceField(
        label=_("Näytettäviä tuloksia"), choices=LIMIT_CHOICES, required=False
    )

    DEFAULT_LANGUAGE = "fi"
    language = forms.ChoiceField(
        label=_("Kieli"), choices=UserSettings.LANGUAGE_CHOICES, required=False
    )

    def filtrate(self, idea_qs):
        idea_qs = super(WidgetIdeaForm, self).filtrate(idea_qs)
        limit = self.cleaned_data.get("limit", None) or self.DEFAULT_LIMIT
        return idea_qs[0:limit]