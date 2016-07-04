# coding=utf-8

from __future__ import unicode_literals

from importlib import import_module

from .conf import config


perms = import_module(config.perms_path)

CanViewSurvey = perms.CanViewSurvey
CanEditSurvey = perms.CanEditSurvey
CanEditSurveyName = perms.CanEditSurveyName
CanAnswerSurvey = perms.CanAnswerSurvey
ShowSurveyResults = perms.ShowSurveyResults
CanViewSurveyModifyMenu = perms.CanViewSurveyModifyMenu
CanOpenSurvey = perms.CanOpenSurvey
CanCloseSurvey = perms.CanCloseSurvey
CanDeleteSurvey = perms.CanDeleteSurvey
OwnsSurvey = perms.OwnsSurvey
SurveyHasAnswers = perms.SurveyHasAnswers