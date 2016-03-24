# coding=utf-8

from __future__ import unicode_literals

from django.contrib.contenttypes.models import ContentType

from libs.moderation.moderator import GenericModerator
from nkmoderation.models import ContentFlag


class BaseModerator(GenericModerator):
    notify_user = False
    notify_moderator = False
    visible_until_rejected = True  # most content is not pre-moderated
    auto_approve_unless_flagged = True
    bypass_moderation_after_approval = True
    moderation_queue_template_name = None

    def is_auto_approve(self, obj, user):
        if self.auto_approve_unless_flagged:
            is_flagged = ContentFlag.objects.filter(
                content_object=obj, status=ContentFlag.STATUS_FLAGGED
            ).count() > 0
            if not is_flagged:
                return self.reason("Auto-approve: no pre-moderation for %s" %
                                   obj._meta.verbos_name_plural)
        return super(BaseModerator, self).is_auto_approve(obj, user)

    def get_moderation_queue_template_name(self):
        if self.moderation_queue_template_name is not None:
            return self.moderation_queue_template_name
        return '%s/%s_moderation.html' % (self.model_class._meta.app_label,
                                          self.model_class._meta.model_name)

    def reject_object(self, moderated_object, moderator=None):
        # by default, destroy the object
        moderated_object.content_object.delete()

    def approve_object(self, moderated_object, moderator=None):
        # by default, no-op
        pass

    def get_object_url(self, obj):
        return obj.get_absolute_url()
