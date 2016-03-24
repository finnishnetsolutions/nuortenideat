# coding=utf-8

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from libs.permitter import perms

from nkvote.models import Vote
from nkvote.utils import get_voter
from nuka import perms as nuka


class OwnsCommentCheck(nuka.BasePermission):
    def __init__(self, **kwargs):
        self.comment = kwargs['obj']
        super(OwnsCommentCheck, self).__init__(**kwargs)

    def is_authorized(self):
        return self.comment.user_id is not None and self.user.pk == self.comment.user_id


OwnsComment = perms.And(nuka.IsAuthenticated, OwnsCommentCheck)


class CommentAlreadyVotedByUser(nuka.BasePermission):
    unauthorized_message = _("Olet jo äänestänyt kommenttia.")

    def __init__(self, **kwargs):
        self.comment = kwargs['obj']
        super(CommentAlreadyVotedByUser, self).__init__(**kwargs)

    def is_authorized(self):
        voter = get_voter(self.request, create=False)
        if voter:
            return Vote.objects.filter(
                voter=voter,
                comments=self.comment
            ).exists()
        else:
            return False


class CommentIsDeleted(nuka.BasePermission):
    unauthorized_message = _("Kommentti on poistettu.")

    def __init__(self, **kwargs):
        self.comment = kwargs['obj']
        super(CommentIsDeleted, self).__init__(**kwargs)

    def is_authorized(self):
        return self.comment.is_deleted()


class CommentIsVoteable(nuka.BasePermission):
    def __init__(self, **kwargs):
        self.initiative = kwargs['obj'].content_object
        super(CommentIsVoteable, self).__init__(**kwargs)

    def is_authorized(self):
        return self.initiative.comments_are_voteable()


class UserIsCommentTargetOrganizationAdmin(nuka.BasePermission):
    def __init__(self, **kwargs):
        self.comment = kwargs['obj']
        super(UserIsCommentTargetOrganizationAdmin, self).__init__(**kwargs)

    def is_authorized(self):
        return self.user.pk in self.comment.content_object.target_organization_admin_ids

CanModerateComment = perms.Or(
    nuka.IsModerator,
    UserIsCommentTargetOrganizationAdmin
)

CanVoteComment = perms.And(
    CommentIsVoteable,
    perms.Not(CommentAlreadyVotedByUser),
    perms.Not(CommentIsDeleted)
)

CanDeleteComment = perms.Or(
    OwnsComment,
    CanModerateComment
)

CanEditComment = CanModerateComment
