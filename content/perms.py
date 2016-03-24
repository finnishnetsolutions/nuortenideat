# coding=utf-8

from __future__ import unicode_literals

from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _, ugettext

from libs.permitter import perms

from account import perms as account
from content.models import Idea, Initiative
from nkvote.models import Vote
from nkvote.utils import get_voter
from nuka import perms as nuka


class OwnsInitiativeCheck(nuka.BasePermission):
    def __init__(self, **kwargs):
        self.initiative = kwargs['obj']
        super(OwnsInitiativeCheck, self).__init__(**kwargs)

    def is_authorized(self):
        return self.user.pk in self.initiative.owner_ids


OwnsInitiative = perms.And(nuka.IsAuthenticated, OwnsInitiativeCheck)


class InitiativeIsPublic(nuka.BasePermission):
    def __init__(self, **kwargs):
        self.initiative = kwargs['obj']
        super(InitiativeIsPublic, self).__init__(**kwargs)

    def get_unauthorized_url(self):
        return reverse('content:initiative_list')

    def is_authorized(self):
        return self.initiative.is_public()


class IdeaIsPublic(InitiativeIsPublic):
    def get_unauthorized_message(self):
        if self.user.is_authenticated():
            msg = _("Idea ei ole vielä julkinen.")
        else:
            msg = ' '.join((ugettext("Idea ei ole vielä julkinen."),
                            ugettext("Kirjaudu sisään, jos olet idean omistaja.")))
        return msg


class IdeaStatusIsPublished(nuka.BasePermission):
    def __init__(self, **kwargs):
        self.idea = kwargs['obj']
        super(IdeaStatusIsPublished, self).__init__(**kwargs)

    def is_authorized(self):
        return self.idea.status == Idea.STATUS_PUBLISHED


class IdeaStatusIsTransferred(nuka.BasePermission):
    def __init__(self, **kwargs):
        self.idea = kwargs['obj']
        super(IdeaStatusIsTransferred, self).__init__(**kwargs)

    def is_authorized(self):
        return self.idea.status == Idea.STATUS_TRANSFERRED


class IdeaNotYetPublished(nuka.BasePermission):
    def __init__(self, **kwargs):
        self.idea = kwargs['obj']
        super(IdeaNotYetPublished, self).__init__(**kwargs)

    def is_authorized(self):
        return self.idea.status < self.idea.__class__.STATUS_PUBLISHED

    unauthorized_message = _("Idea on jo julkaistu.")

    def get_unauthorized_url(self):
        return reverse('content:idea_detail', kwargs={'initiative_id': self.idea.pk})


class IdeaIsEditable(nuka.BasePermission):
    def __init__(self, **kwargs):
        self.idea = kwargs['obj']
        super(IdeaIsEditable, self).__init__(**kwargs)

    def is_authorized(self):
        if self.idea.status >= Idea.STATUS_TRANSFERRED:
            return False
        return not self.idea.is_locked


class IdeaVotedByUser(nuka.BasePermission):
    def __init__(self, **kwargs):
        self.idea = kwargs['obj']
        super(IdeaVotedByUser, self).__init__(**kwargs)

    def is_authorized(self):
        voter = get_voter(self.request, create=False)
        if voter:
            return Vote.objects.filter(
                voter=voter,
                ideas=self.idea
            ).exists()
        else:
            return False


class InitiativeModelInit(nuka.BasePermission):
    def __init__(self, **kwargs):
        self.model_name = kwargs['obj'].__class__.__name__
        super(InitiativeModelInit, self).__init__(**kwargs)


class IsQuestion(InitiativeModelInit):
    def is_authorized(self):
        return self.model_name == 'Question'


class IsIdea(InitiativeModelInit):
    def is_authorized(self):
        return self.model_name == 'Idea'


class IdeaTargetMunicipalityParticipatesInKUA(nuka.BasePermission):
    def __init__(self, **kwargs):
        self.idea = kwargs['obj']
        super(IdeaTargetMunicipalityParticipatesInKUA, self).__init__(**kwargs),

    def is_authorized(self):
        org = self.idea.target_municipality
        if org is None:
            return False
        return org.participates_in_kua()


class UserBelongsToIdeasTargetMunicipality(nuka.BasePermission):
    def __init__(self, **kwargs):
        self.idea = kwargs['obj']
        super(UserBelongsToIdeasTargetMunicipality, self).__init__(**kwargs)

    def is_authorized(self):
        m = self.idea.target_municipality.municipalities.first()
        return m is not None and self.request.user.settings.municipality.pk == m.pk


class InitiativeIsNotArchived(nuka.BasePermission):
    def __init__(self, **kwargs):
        self.initiative = kwargs['obj']
        super(InitiativeIsNotArchived, self).__init__(**kwargs)

    def is_authorized(self):
        return self.initiative.visibility != Initiative.VISIBILITY_ARCHIVED


class IdeaCanBeArchived(nuka.BasePermission):
    def __init__(self, **kwargs):
        self.idea = kwargs['obj']
        super(IdeaCanBeArchived, self).__init__(**kwargs)

    def is_authorized(self):
        allowed_statuses = [Idea.STATUS_PUBLISHED, Idea.STATUS_DECISION_GIVEN]
        return self.idea.status in allowed_statuses and \
            self.idea.visibility != Idea.VISIBILITY_ARCHIVED


class InitiativeInteractionRegistered(nuka.BasePermission):
    def __init__(self, **kwargs):
        self.initiative = kwargs['obj']
        super(InitiativeInteractionRegistered, self).__init__(**kwargs)

    def is_authorized(self):
        return self.initiative.interaction == Initiative.INTERACTION_REGISTERED_USERS


class UserIsInitiativeTargetOrganizationAdminCheck(nuka.BasePermission):
    def __init__(self, **kwargs):
        self.initiative = kwargs['obj']
        super(UserIsInitiativeTargetOrganizationAdminCheck, self).__init__(**kwargs)

    def is_authorized(self):
        return len(set(self.initiative.target_organization_ids)
                   & set(self.request.user.organization_ids)) > 0

UserIsInitiativeTargetOrganizationAdmin = perms.And(
    nuka.IsAuthenticated,
    UserIsInitiativeTargetOrganizationAdminCheck
)


class KuaApiIsEnabled(nuka.BasePermission):
    unauthorized_message = _("Kuntalaisaloite.fi-integraatio on kytketty pois päältä.")

    def is_authorized(self):
        return settings.KUA_API['enabled']


class CanVoteInitiative(nuka.BasePermission):
    def __init__(self, **kwargs):
        self.obj = kwargs['obj']
        super(CanVoteInitiative, self).__init__(**kwargs)

    def is_authorized(self):
        return self.obj.is_voteable()


CanModerateInitiative = perms.And(
    nuka.IsAuthenticated,
    perms.Or(nuka.IsModerator, UserIsInitiativeTargetOrganizationAdmin),
)
CanModerateIdea = CanModerateQuestion = CanModerateInitiative

CanUnArchiveIdea = perms.And(
    perms.Not(InitiativeIsNotArchived),
    CanModerateIdea
)

CanArchiveIdea = perms.And(
    perms.Or(
        OwnsInitiative,
        CanModerateIdea
    ),
    IdeaCanBeArchived
)

CanEditIdea = perms.And(
    nuka.IsAuthenticated,
    InitiativeIsNotArchived,
    perms.Or(
        perms.And(OwnsInitiative, IdeaIsEditable),
        CanModerateIdea
    )
)

CanViewIdea = perms.Or(
    perms.And(IdeaIsPublic, InitiativeIsNotArchived),
    perms.And(
        nuka.IsAuthenticated,
        perms.Or(OwnsInitiative, CanModerateIdea)
    )
)

CanPublishIdea = perms.And(CanEditIdea, IdeaNotYetPublished)

CanSeeAllInitiatives = perms.Or(account.OwnAccount,
                                nuka.IsModerator)

CanAddIdeaDetails = perms.And(
    nuka.IsAuthenticated,
    perms.And(
        perms.Or(
            perms.And(OwnsInitiative, perms.Not(IdeaIsEditable)),
            CanModerateIdea
        ),
        InitiativeIsNotArchived
    )
)

CanDeleteIdea = perms.And(
    nuka.IsAuthenticated,
    perms.Or(
        perms.And(OwnsInitiative, IdeaIsEditable),
        CanModerateIdea
    )
)

CanVoteIdea = perms.And(
    IdeaIsPublic,
    CanVoteInitiative,
    perms.Not(IdeaVotedByUser),
    perms.Or(
        perms.Not(InitiativeInteractionRegistered),
        perms.And(
            InitiativeInteractionRegistered,
            nuka.IsAuthenticated
        )
    )
)

CanEditQuestion = perms.And(nuka.IsAuthenticated, CanModerateQuestion)

CanCreateIdeaFromQuestion = perms.Or(
    CanModerateIdea,
    OwnsInitiative
)

CanEditInitiative = perms.Or(
    perms.And(IsIdea, CanEditIdea),
    perms.And(IsQuestion, CanEditQuestion),
)

CanDeleteQuestion = perms.And(nuka.IsAuthenticated, CanModerateQuestion)

CanChangeIdeaSettings = perms.And(
    nuka.IsAuthenticated,
    perms.Or(OwnsInitiative, CanModerateIdea),
    InitiativeIsNotArchived
)

CanCreatePdf = CanChangeIdeaSettings

CanViewQuestionTools = perms.Or(CanDeleteQuestion, CanCreateIdeaFromQuestion)

CanViewIdeaTools = perms.Or(
    CanChangeIdeaSettings,
    CanArchiveIdea,
    CanUnArchiveIdea
)

CanTransferIdeaForward = perms.And(
    perms.Or(
        OwnsInitiative,
        CanModerateIdea
    ),
    IdeaStatusIsPublished
)

CanTransferIdeaToKUA = perms.And(
    CanTransferIdeaForward,
    OwnsInitiative,
    IdeaTargetMunicipalityParticipatesInKUA,
    KuaApiIsEnabled
)

CanTransferIdeaToKUAWithoutExtraAction = perms.And(
    CanTransferIdeaToKUA,
    account.UserEmailSpecified
)

CanTransferIdeaToKUAWithoutExtraConfirmation = perms.And(
    CanTransferIdeaToKUAWithoutExtraAction,
    UserBelongsToIdeasTargetMunicipality
)

CanPublishIdeaDecision = perms.And(
    nuka.IsAuthenticated,
    perms.Or(
        OwnsInitiative,
        CanModerateIdea
    ),
    IdeaStatusIsTransferred
)

CanCommentInitiative = perms.And(
    InitiativeIsPublic,
    InitiativeIsNotArchived,
    perms.Or(
        perms.Not(InitiativeInteractionRegistered),
        nuka.IsAuthenticated,
    )
)
