# coding=utf-8

from __future__ import unicode_literals

from polymorphic.manager import PolymorphicManager

from libs.moderation import moderation
from libs.moderation.managers import ModerationObjectsManager

from .models import Initiative, Idea, Question

from nuka.moderator import BaseModerator


class ModerationPolymorphicManager(ModerationObjectsManager, PolymorphicManager):
    pass


class InitiativeManager(ModerationPolymorphicManager):
    def filter_moderated_objects(self, query_set):
        # TODO: if initiatives need pre-moderation, add VISIBILITY_PENDING_MODERATION
        # and set it at PublishIdeaView
        return query_set.filter(visibility=Initiative.VISIBILITY_PUBLIC)


class IdeaModerator(BaseModerator):
    moderation_manager_class = InitiativeManager


class QuestionModerator(BaseModerator):
    moderation_manager_class = InitiativeManager


moderation.register(Idea, IdeaModerator)
moderation.register(Question, QuestionModerator)
