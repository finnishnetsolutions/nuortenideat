# coding=utf-8

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from survey.apps import SurveyAppConfig


class NukaSurveyAppConfig(SurveyAppConfig):
    SHOW_RESULTS_OWNERS = 3

    perms_path = "content.survey_perms"
    base_permission_class = "nuka.perms.BasePermission"
    show_results_choices = SurveyAppConfig.show_results_choices + (
        (SHOW_RESULTS_OWNERS, _("Omistajat")),
    )
    show_results_default = SHOW_RESULTS_OWNERS
    client_identifier_path = "account.ClientIdentifier"
    get_client_identifier_path = "account.utils.get_client_identifier"

