# coding=utf-8

from __future__ import unicode_literals

from django.db import models
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.utils import timezone

from account.models import ClientIdentifier
from content.models import Idea
from libs.multilingo.models import fields as multilingo


class Voter(models.Model):
    VOTER_COOKIE = "joku"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, default=None,
                             unique=True)
    voter_id = models.CharField(max_length=32, unique=True)
    created = models.DateTimeField(default=timezone.now)


class VoteQuerySet(models.QuerySet):
    def up(self):
        return self.filter(choice=Vote.VOTE_UP)

    def down(self):
        return self.filter(choice=Vote.VOTE_DOWN)

    def filter(self, *args, **kwargs):
        if kwargs.has_key('content_object'):
            content_object = kwargs.pop('content_object')
            content_type = ContentType.objects.get_for_model(content_object)
            kwargs.update({
                'content_type': content_type,
                'object_id': content_object.pk
            })
        return super(VoteQuerySet, self).filter(*args, **kwargs)


class Vote(models.Model):
    VOTE_UP = 1
    VOTE_DOWN = -1
    VOTE_NONE = 0

    voter = models.ForeignKey(Voter)
    client_identifier = models.ForeignKey(ClientIdentifier)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    created = models.DateTimeField(auto_now_add=True)
    choice = models.SmallIntegerField()

    objects = VoteQuerySet.as_manager()

    @classmethod
    def votes_for(cls, model, instance=None):
        ct = ContentType.objects.get_for_model(model)
        kwargs = {"content_type": ct}
        if instance is not None:
            kwargs["object_id"] = instance.pk
        return cls.objects.filter(**kwargs)

    class Meta:
        unique_together = ('voter', 'content_type', 'object_id')


class Gallup(models.Model):
    STATUS_DRAFT = 1
    STATUS_OPEN = 5
    STATUS_CLOSED = 10

    # Indicates if the gallup shows results or questions by default.
    DEFAULT_QUESTIONS = 1
    DEFAULT_RESULTS = 2

    idea = models.ForeignKey(Idea)
    status = models.SmallIntegerField(default=STATUS_DRAFT)
    default_view = models.SmallIntegerField(default=DEFAULT_QUESTIONS)

    created = models.DateTimeField(auto_now_add=True)
    opened = models.DateTimeField(null=True)
    closed = models.DateTimeField(null=True)

    def default_results(self):
        return self.default_view == self.DEFAULT_RESULTS

    def is_open(self):
        return self.status == self.STATUS_OPEN

    def is_draft(self):
        return self.status == self.STATUS_DRAFT

    def is_closed(self):
        return self.status == self.STATUS_CLOSED


class Question(models.Model):
    gallup = models.ForeignKey(Gallup)
    text = multilingo.MultilingualTextField(_("kysymys"))
    seq_number = models.PositiveSmallIntegerField(default=1)

    def total_answers_count(self):
        answers = 0
        for option in self.option_set.all():
            answers += option.answers_count()
        return answers

    class Meta:
        ordering = ["gallup", "seq_number"]


@python_2_unicode_compatible
class Option(models.Model):
    question = models.ForeignKey(Question)
    text = multilingo.MultilingualTextField(_("vaihtoehto"))
    seq_number = models.PositiveSmallIntegerField(default=1)

    def answers_count(self):
        return self.answer_set.all().count()

    def percentage_of_question(self):
        total = self.question.total_answers_count()
        if total == 0:
            return 0
        share = self.answers_count()
        percentage = float(share)/float(total)*100.0
        return "%.1f" % round(percentage, 1)

    def __str__(self):
        return 'Question #%d: %s' % (self.question_id, self.text)

    class Meta:
        ordering = ["question", "seq_number"]


class Answer(models.Model):
    gallup = models.ForeignKey(Gallup)
    choices = models.ManyToManyField(Option)

    voter = models.ForeignKey(Voter)
    client_identifier = models.ForeignKey(ClientIdentifier)

    submit_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('voter', 'gallup')