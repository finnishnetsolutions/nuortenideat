# coding=utf-8

from __future__ import unicode_literals

from django.contrib.comments.models import Comment

from libs.moderation import moderation

from nuka.moderator import BaseModerator
from nkmoderation.models import ContentFlag

from .models import CustomComment


class CommentModerator(BaseModerator):
    moderation_queue_template_name = 'nkcomments/comment_moderation.html'
    auto_approve_unless_flagged = True
    visibility_column = 'is_public'

    def get_object_url(self, obj):
        # Because Comment.get_absolute_url() sucks.
        return obj.content_object.get_absolute_url() + '#c%d' % obj.pk

    def is_auto_approve(self, obj, user):
        if getattr(self.obj.content_object, 'premoderation', False) is True:
            # Pre-moderation needed - bypass BaseModerator, so it won't auto-approve
            # despite auto_approve_unless_flagged = True.
            #
            # moderation.GenericModerator may still auto approve e.g. based on user role
            return super(BaseModerator, self).is_auto_approve(obj, user)

        # premoderation not enabled - roll as usual taking auto_approve_unless_flagged
        # into account
        return super(CommentModerator, self).is_auto_approve(obj, user)

    def reject_object(self, moderated_object, moderator=None):
        if moderated_object.content_object.content_object.premoderation and not \
                ContentFlag.objects.is_flagged(moderated_object.content_object):
            super(CommentModerator, self).reject_object(moderated_object, moderator)
        else:
            moderated_object.content_object.flags.create(
                user=moderator,
                flag=CustomComment.FLAG_DELETED,
            )

    def approve_object(self, moderated_object, moderator=None):
        moderated_object.content_object.is_public = True
        moderated_object.content_object.save()


moderation.register(Comment, CommentModerator)
moderation.register(CustomComment, CommentModerator)
