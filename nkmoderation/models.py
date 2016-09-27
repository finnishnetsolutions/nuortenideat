# coding=utf-8

from __future__ import unicode_literals

from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch.dispatcher import receiver
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from account.models import User, GROUP_NAME_MODERATORS, GROUP_NAME_ADMINS
from actions.models import ActionGeneratingModelMixin

from libs.moderation.models import ModeratedObject, MODERATION_STATUS_APPROVED, \
    MODERATION_STATUS_PENDING


class ContentFlagQuerySet(models.QuerySet):
    def is_flagged(self, obj):
        return self.filter(content_type=ContentType.objects.get_for_model(obj),
                           object_id=obj.pk,
                           status=ContentFlag.STATUS_FLAGGED)[:1].count()


class ContentFlag(ActionGeneratingModelMixin, models.Model):
    STATUS_FLAGGED = 1
    STATUS_FLAG_REJECTED = 2
    STATUS_FLAG_APPROVED = 3

    STATUS_CHOICES = (
        (STATUS_FLAGGED,            _("ilmoitettu")),
        (STATUS_FLAG_REJECTED,      _("ilmoitus hylätty")),
        (STATUS_FLAG_APPROVED,      _("ilmoitus hyväksytty")),
    )

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()

    content_object = generic.GenericForeignKey('content_type', 'object_id')

    flagger = models.ForeignKey('account.User', related_name='flagged_content', null=True,
                                verbose_name=_("ilmoittaja"))
    client_identifier = models.ForeignKey('account.ClientIdentifier',
                                          related_name='flagged_content')

    reason = models.CharField(_("syy ilmoitukseen"), max_length=250,
                              help_text=_("Kerro lyhyesti, mikä tekee sisällöstä "
                                          "asiattoman. Enintään %d merkkiä.") % 250)
    status = models.SmallIntegerField(_("tila"), choices=STATUS_CHOICES,
                                      default=STATUS_FLAGGED)
    created = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(default=timezone.now)

    objects = ContentFlagQuerySet.as_manager()

    def action_kwargs_on_create(self):
        return {'actor': self.flagger, }

    def fill_notification_recipients(self, action):
        for u in User.objects.filter(groups__name__in=[GROUP_NAME_MODERATORS,
                                                       GROUP_NAME_ADMINS]):
            action.add_notification_recipients(action.ROLE_MODERATOR, u)

    class Meta:
        unique_together = (
            ('flagger', 'content_type', 'object_id', ),
            ('client_identifier', 'content_type', 'object_id', ),
        )


class ModerationReason(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    timestamp = models.DateTimeField(default=timezone.now)
    reason = models.CharField(max_length=250)

    moderator = models.ForeignKey('account.User', related_name='moderated_content')

    class Meta:
        index_together = (('content_type', 'object_id', ),)


@receiver(signal=pre_save, sender=ModeratedObject)
def auto_approval(instance=None, **kwargs):
    if instance.pk is None:
        if instance.moderator.visibility_column is not None:
            # auto-approve if instance is pre-marked as active based on visibility_column
            # e.g. when generating test data with ModelFactories
            if getattr(instance.content_object, instance.moderator.visibility_column,
                       False) is True:
                instance.moderation_status = MODERATION_STATUS_APPROVED
        elif instance.moderator.auto_approve_unless_flagged and \
                not getattr(instance, '_flagged', False):
            instance.moderation_status = MODERATION_STATUS_APPROVED


@receiver(signal=post_save, sender=ContentFlag)
def send_flagged_content_to_moderation_queue(instance=None, created=False, **kwargs):
    if created:
        try:
            mo = ModeratedObject.objects.get_for_instance(instance.content_object)
        except ModeratedObject.DoesNotExist:
            mo = ModeratedObject(content_object=instance.content_object)

        mo.moderation_status = MODERATION_STATUS_PENDING
        mo._flagged = True  # HACK to prevent auto-approval
        mo.save()
