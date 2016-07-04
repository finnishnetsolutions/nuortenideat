# coding=utf-8

from __future__ import unicode_literals
from django.http.response import JsonResponse

from django.utils.module_loading import import_string
from django.utils.translation import ugettext_lazy as _

from libs.permitter import perms

from .conf import config
from .utils import get_submitter


BasePermission = import_string(config.base_permission_class)


class BaseSurveyPermission(BasePermission):
    def __init__(self, **kwargs):
        self.survey = kwargs["obj"]
        super(BaseSurveyPermission, self).__init__(**kwargs)

    def is_authorized(self):
        raise NotImplementedError()


class SurveyHasAnswers(BaseSurveyPermission):
    unauthorized_message = _("Kyselyssä on jo vastauksia.")

    def get_unauthorized_response(self):
        super(SurveyHasAnswers, self).get_unauthorized_response()
        return JsonResponse({'reload': True})

    def is_authorized(self):
        return self.survey.submissions.exists()


class SurveyAnsweredByUser(BaseSurveyPermission):
    unauthorized_message = _("Olet jo vastannut kyselyyn.")

    def is_authorized(self):
        submitter = get_submitter(self.request, create=False)
        if submitter:
            return self.survey.submissions.filter(submitter=submitter).exists()
        else:
            return False


class SurveyShowResultsEveryone(BaseSurveyPermission):
    def is_authorized(self):
        assert hasattr(config, "SHOW_RESULTS_EVERYONE"), \
            "Current survey configuration does not have SHOW_RESULTS_EVERYONE. " \
            "Permmission can't be used."
        return self.survey.show_results == config.SHOW_RESULTS_EVERYONE


class SurveyShowResultsAnsweredUsers(BaseSurveyPermission):
    def is_authorized(self):
        assert hasattr(config, "SHOW_RESULTS_ANSWERED"), \
            "Current survey configuration does not have SHOW_RESULTS_ANSWERED. " \
            "Permmission can't be used."
        return self.survey.show_results == config.SHOW_RESULTS_ANSWERED


class AllowAll(BaseSurveyPermission):
    def is_authorized(self):
        return True


CanEditSurvey = perms.And(
    perms.Not(SurveyHasAnswers),
)

CanAnswerSurvey = perms.And(
    perms.Not(SurveyAnsweredByUser),
)

ShowSurveyResults = perms.Or(
    SurveyShowResultsEveryone,
    perms.And(SurveyShowResultsAnsweredUsers, SurveyAnsweredByUser),
)
