# coding=utf-8

from __future__ import unicode_literals

from django.contrib.contenttypes.models import ContentType

from libs.permitter import perms

from nuka import perms as nuka
from survey import default_perms
from survey.conf import config as survey_config
from survey.models import Survey

from .models import IdeaSurvey
from .perms import CanParticipateSurvey


class BaseSurveyPermissionExtended(default_perms.BaseSurveyPermission):
    def __init__(self, **kwargs):
        super(BaseSurveyPermissionExtended, self).__init__(**kwargs)
        self.idea_survey = IdeaSurvey.objects.get(
            object_id=self.survey.pk,
            content_type=ContentType.objects.get_for_model(Survey)
        )

    def is_authorized(self):
        raise NotImplementedError()


class SurveyShowResultsOwners(default_perms.BaseSurveyPermission):
    def is_authorized(self):
        return self.survey.show_results == survey_config.SHOW_RESULTS_OWNERS


class OwnsSurvey(BaseSurveyPermissionExtended):
    def is_authorized(self):
        return self.user.pk in self.idea_survey.idea.owner_ids


class SurveyIsDraft(BaseSurveyPermissionExtended):
    def is_authorized(self):
        return self.idea_survey.is_draft()


class SurveyIsClosed(BaseSurveyPermissionExtended):
    def is_authorized(self):
        return self.idea_survey.is_closed()


class SurveyIsOpen(BaseSurveyPermissionExtended):
    def is_authorized(self):
        if self.idea_survey.is_open():
            return CanParticipateSurvey(
                request=self.request, obj=self.idea_survey).is_authorized()
        return False


class SurveyInteractionEveryone(BaseSurveyPermissionExtended):
    def is_authorized(self):
        return self.idea_survey.interaction == IdeaSurvey.INTERACTION_EVERYONE


class SurveyInitiativeIsPublic(BaseSurveyPermissionExtended):
    def is_authorized(self):
        return self.idea_survey.idea.is_public()


class SurveyHasAnswers(BaseSurveyPermissionExtended):
    def is_authorized(self):
        return self.survey.submissions.exists()


CanEditSurvey = perms.And(
    default_perms.CanEditSurvey,
    perms.Or(OwnsSurvey, nuka.IsModerator),
)

CanEditSurveyName = perms.Or(OwnsSurvey, nuka.IsModerator)

CanAnswerSurvey = perms.And(
    default_perms.CanAnswerSurvey,
    SurveyIsOpen,
    perms.Not(OwnsSurvey),
    perms.Or(
        nuka.IsAuthenticated,
        SurveyInteractionEveryone
    )
)

ShowSurveyResults = perms.Or(
    OwnsSurvey,
    default_perms.ShowSurveyResults,
    perms.And(SurveyShowResultsOwners, OwnsSurvey),
)

CanViewSurvey = perms.Or(
    perms.Not(SurveyIsDraft),
    perms.Or(OwnsSurvey, nuka.IsModerator)
)

CanViewSurveyModifyMenu = perms.Or(OwnsSurvey, nuka.IsModerator)

CanOpenSurvey = perms.And(
    SurveyInitiativeIsPublic,
    perms.Or(
        perms.And(SurveyIsDraft, OwnsSurvey),
        perms.And(
            perms.Or(SurveyIsDraft, SurveyIsClosed),
            nuka.IsModerator
        ),
    )
)

CanCloseSurvey = perms.And(
    SurveyIsOpen,
    perms.Or(OwnsSurvey, nuka.IsModerator)
)

CanDeleteSurvey = perms.Or(
    perms.And(
        perms.Not(SurveyHasAnswers),
        OwnsSurvey
    ),
    nuka.IsModerator
)
