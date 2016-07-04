# coding=utf-8

from __future__ import unicode_literals

from libs.permitter import perms

from content.models import Idea
from content.perms import OwnsInitiative, InitiativeIsNotArchived
from nkvote.models import Gallup
from nkvote.utils import answered_gallup
from nuka import perms as nuka


class OwnsGallup(nuka.BasePermission):
    def __init__(self, **kwargs):
        self.gallup = kwargs['obj']
        super(OwnsGallup, self).__init__(**kwargs)

    def is_authorized(self):
        if self.user in self.gallup.idea.owners.all():
            return True
        elif self.gallup.idea.initiator_organization:
            if self.user in self.gallup.idea.initiator_organization.admins.all():
                return True
        else:
            return False


class GallupIsDraft(nuka.BasePermission):
    def __init__(self, **kwargs):
        self.gallup = kwargs['obj']
        super(GallupIsDraft, self).__init__(**kwargs)

    def is_authorized(self):
        return self.gallup.is_draft()


class GallupIsOpen(nuka.BasePermission):
    def __init__(self, **kwargs):
        self.gallup = kwargs['obj']
        super(GallupIsOpen, self).__init__(**kwargs)

    def is_authorized(self):
        return self.gallup.is_open()


class GallupIsClosed(nuka.BasePermission):
    def __init__(self, **kwargs):
        self.gallup = kwargs['obj']
        super(GallupIsClosed, self).__init__(**kwargs)

    def is_authorized(self):
        return self.gallup.is_closed()


class GallupAnswered(nuka.BasePermission):
    def __init__(self, **kwargs):
        self.gallup = kwargs['obj']
        super(GallupAnswered, self).__init__(**kwargs)

    def is_authorized(self):
        return answered_gallup(self.request, self.gallup)


class AnsweringGallupRequiresLogin(nuka.BasePermission):
    def __init__(self, **kwargs):
        self.gallup = kwargs['obj']
        super(AnsweringGallupRequiresLogin, self).__init__(**kwargs)

    def is_authorized(self):
        return self.gallup.interaction == Gallup.INTERACTION_REGISTERED_USERS


class GallupHasAnswers(nuka.BasePermission):
    def __init__(self, **kwargs):
        self.gallup = kwargs["obj"]
        super(GallupHasAnswers, self).__init__(**kwargs)

    def is_authorized(self):
        return self.gallup.answer_set.all().count() > 0


class GallupInitiativeIsPublic(nuka.BasePermission):
    def __init__(self, **kwargs):
        self.gallup = kwargs["obj"]
        super(GallupInitiativeIsPublic, self).__init__(**kwargs)

    def is_authorized(self):
        return self.gallup.idea.is_public()


# Requires initiative id (obj_by_pk(Initiative, 'initiative_id')).
CanCreateGallup = perms.And(
    InitiativeIsNotArchived,
    perms.Or(OwnsInitiative, nuka.IsModerator)
)

CanAnswerGallup = perms.And(
    GallupIsOpen,
    perms.Not(GallupAnswered),
    perms.Or(
        perms.Not(AnsweringGallupRequiresLogin),
        perms.And(
            AnsweringGallupRequiresLogin,
            nuka.IsAuthenticated
        )
    )
)

CanViewGallup = perms.Or(
    perms.Not(GallupIsDraft),
    perms.Or(OwnsGallup, nuka.IsModerator)
)

CanSeeGallupModifyMenu = perms.Or(OwnsGallup, nuka.IsModerator)

CanEditGallup = perms.Or(
    perms.And(
        perms.Not(GallupIsClosed),
        perms.Not(GallupHasAnswers),
        OwnsGallup
    ),
    nuka.IsModerator
)

CanOpenGallup = perms.And(
    GallupInitiativeIsPublic,
    perms.Or(
        perms.And(GallupIsDraft, OwnsGallup),
        perms.And(
            perms.Or(GallupIsDraft, GallupIsClosed),
            nuka.IsModerator
        ),
    )
)

CanCloseGallup = perms.And(
    GallupIsOpen,
    perms.Or(OwnsGallup, nuka.IsModerator)
)

CanDeleteGallup = perms.Or(
    perms.And(
        perms.Not(GallupHasAnswers),
        OwnsGallup
    ),
    nuka.IsModerator
)
