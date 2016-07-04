# coding=utf-8

from __future__ import unicode_literals

from django.apps.config import AppConfig
from django.utils.translation import ugettext_lazy as _


class SurveyAppConfig(AppConfig):
    name = "survey"

    SHOW_RESULTS_EVERYONE = 1
    SHOW_RESULTS_ANSWERED = 2

    perms_path = "survey.default_perms"
    base_permission_class = "libs.permitter.perms.FriendlyRequestPermission"
    show_results_choices = (
        (SHOW_RESULTS_EVERYONE, _("Kaikki")),
        (SHOW_RESULTS_ANSWERED, _("Vastanneet")),
    )
    show_results_default = SHOW_RESULTS_ANSWERED
