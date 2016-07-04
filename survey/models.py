# coding=utf-8

from __future__ import unicode_literals

from uuid import uuid4

from ordered_model.models import OrderedModel
from polymorphic.manager import PolymorphicManager
from polymorphic.polymorphic_model import PolymorphicModel

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from libs.multilingo.models.fields import MultilingualTextField

from .conf import config


class Survey(models.Model):
    show_results = models.SmallIntegerField(verbose_name=_("Vastausten näyttäminen"),
                                            null=True)

    def get_show_results_display(self):
        choices = dict(config.show_results_choices)
        return choices[self.show_results]

    def get_involved_user_ids(self):
        submissions = self.submissions.filter(submitter__user_id__isnull=False)
        return [s.survey_submitter.user_id for s in submissions]


class SurveyElementManager(PolymorphicManager):
    def questions(self):
        qs = self.get_queryset()
        return qs.instance_of(SurveyQuestion)

    def pages(self):
        qs = self.get_queryset()
        return qs.instance_of(SurveyPage)


class SurveyElement(PolymorphicModel, OrderedModel):
    survey = models.ForeignKey(Survey, related_name="elements")

    objects = SurveyElementManager()
    order_with_respect_to = "survey"

    def get_ordering_queryset(self, qs=None):
        if qs is None:
            qs = SurveyElement.objects.all()
        return super(SurveyElement, self).get_ordering_queryset(qs)

    class Meta(PolymorphicModel.Meta, OrderedModel.Meta):
        pass


class SurveyPage(SurveyElement):
    pass


class SurveySubtitle(SurveyElement):
    text = MultilingualTextField(_("väliotsikko"), max_length=255, simultaneous_edit=True)


class SurveyQuestion(SurveyElement):
    TYPE_RADIO = 1
    TYPE_CHECKBOX = 2
    TYPE_TEXT = 3
    TYPE_NUMBER = 4
    TYPE_CHOICES = (
        (TYPE_RADIO, _("Yksivalinta")),
        (TYPE_CHECKBOX, _("Monivalinta")),
        (TYPE_TEXT, _("Tekstikenttä")),
        (TYPE_NUMBER, _("Numerokenttä")),
    )
    TYPE_MULTIPLE_VALUES = (
        TYPE_CHECKBOX,
    )

    text = MultilingualTextField(_("kysymys"), max_length=255, simultaneous_edit=True)
    instruction_text = MultilingualTextField(_("ohjeteksti"), max_length=800, blank=True,
                                             simultaneous_edit=True)
    required = models.BooleanField(blank=True, verbose_name=_("pakollinen"),
                                   default=False)
    type = models.IntegerField(choices=TYPE_CHOICES)

    def is_option_input(self):
        return self.type in [self.TYPE_RADIO, self.TYPE_CHECKBOX]

    def __str__(self):
        return "{}".format(self.text)


class SurveyOption(OrderedModel):
    question = models.ForeignKey(SurveyQuestion, related_name="options")
    text = MultilingualTextField(_("vaihtoehto"), max_length=255, simultaneous_edit=True,
                                 null=True, blank=True)

    order_with_respect_to = "question"

    def __str__(self):
        return "{}".format(self.text)


def create_submitter_id():
    return uuid4().hex


class SurveySubmitter(models.Model):
    SUBMITTER_COOKIE = "surveysubmitter"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name="survey_submitter",
                                null=True, default=None)
    submitter_id = models.CharField(max_length=32, unique=True,
                                    default=create_submitter_id)
    created = models.DateTimeField(default=timezone.now)


class SurveySubmission(models.Model):
    survey = models.ForeignKey(Survey, related_name="submissions")
    # TODO: null=False
    submitter = models.ForeignKey(SurveySubmitter, null=True)
    # TODO: null=False
    client_identifier = models.ForeignKey(config.client_identifier_path, null=True)
    created = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("survey", "submitter")


class SurveyAnswerQuerySet(models.QuerySet):
    def paginate(self, page=1, count=None):
        if count is None:
            count = SurveyAnswer.PAGINATE_BY
        paginator = Paginator(self, count)
        try:
            answers = paginator.page(page)
        except PageNotAnInteger:
            answers = paginator.page(1)
        except EmptyPage:
            answers = paginator.page(paginator.num_pages)
        return answers


class SurveyAnswer(models.Model):
    PAGINATE_BY = 10

    submission = models.ForeignKey(SurveySubmission, related_name="answers")
    question = models.ForeignKey(SurveyQuestion, related_name="answers")
    option = models.ForeignKey(SurveyOption, related_name="answers", null=True)
    text = models.CharField(max_length=10000, blank=True, null=True)

    objects = SurveyAnswerQuerySet.as_manager()
