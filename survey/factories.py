# coding=utf-8

from __future__ import unicode_literals

import factory

from account.factories import ClientIdentifierFactory

from . import models


class SurveyFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Survey


class SurveySubmitterFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.SurveySubmitter


class SurveySubmissionFactory(factory.DjangoModelFactory):
    survey = factory.SubFactory(SurveyFactory)
    submitter = factory.SubFactory(SurveySubmitterFactory)
    client_identifier = factory.SubFactory(ClientIdentifierFactory)

    class Meta:
        model = models.SurveySubmission


class SurveyElementFactory(factory.DjangoModelFactory):
    survey = factory.SubFactory(SurveyFactory)

    class Meta:
        model = models.SurveyElement


class SurveyQuestionFactory(SurveyElementFactory):
    text = factory.Sequence(lambda x: "Is it question {}?".format(x))
    required = False
    type = models.SurveyQuestion.TYPE_TEXT

    class Meta:
        model = models.SurveyQuestion
