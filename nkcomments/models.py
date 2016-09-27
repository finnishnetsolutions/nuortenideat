# coding=utf-8

from __future__ import unicode_literals
from django.contrib.contenttypes.models import ContentType

from django.db import models
from django_comments.models import Comment
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver

from actions.models import ActionGeneratingModelMixin
from nuka.utils import strip_tags


class CommentQuerySet(models.QuerySet):
    def public(self):
        id_list = [c.pk for c in self.all() if not c.is_deleted()]
        return self.filter(pk__in=id_list)


class CustomComment(Comment, ActionGeneratingModelMixin):

    FLAG_DELETED = "deleted"
    votes = GenericRelation("nkvote.Vote", related_query_name="comments")
    objects = CommentQuerySet.as_manager()

    def comment_plaintext(self):
        return strip_tags(self.comment)

    def is_deleted(self):
        if self.flags.filter(flag=self.FLAG_DELETED).first():
            return True
        return False

    def mark_deleted(self, deleting_user):
        if self.is_deleted():
            return True

        self.flags.get_or_create(
            user=deleting_user,
            flag=self.FLAG_DELETED,
        )

    def unmark_deleted(self):
        if not self.is_deleted():
            return True

        deleted_flag = self.flags.get(flag=self.FLAG_DELETED)
        self.flags.remove(deleted_flag)

    def highlight(self):
        if self.user_id is None:
            return False

        if self.user_id in self.content_object.owner_ids:
            return True

        if self.user_organizations.count():
            return True

        return False

    # for moderation
    @property
    def owner_ids(self):
        return [self.user.pk] if self.user_id else []

    def get_absolute_url(self):
        return self.content_object.get_absolute_url() + '#c%d' % self.pk

    def is_anonymous(self):
        return self.user_id is None

    # action processing
    ACTION_SUB_TYPE_IDEA_COMMENTED = 'idea-commented'
    ACTION_SUB_TYPE_QUESTION_COMMENTED = 'question-commented'
    ACTION_SUB_TYPE_QUESTION_ANSWERED = 'question-answered'

    def action_kwargs_on_create(self):
        if self.content_object.is_idea():
            subtype = CustomComment.ACTION_SUB_TYPE_IDEA_COMMENTED
        else:
            if self.user in self.content_object.organization.admins.all():
                subtype = CustomComment.ACTION_SUB_TYPE_QUESTION_ANSWERED
            else:
                subtype = CustomComment.ACTION_SUB_TYPE_QUESTION_COMMENTED
        return {'actor': self.user, 'subtype': [subtype]}

    def fill_notification_recipients(self, action):
        self.content_object.fill_notification_recipients(action)

    def fill_anonymous_notification_recipients(self, action):
        self.content_object.fill_anonymous_notification_recipients(action)

    class Meta:
        proxy = True
        ordering = ('submit_date', )


class CommentUserOrganisations(models.Model):

    comment = models.ForeignKey(CustomComment, related_name='user_organizations')
    organization = models.ForeignKey('organization.Organization', related_name='comments')

    class Meta:
        unique_together = (('comment', 'organization'), )
