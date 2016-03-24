# coding=utf-8

from __future__ import unicode_literals

from libs.moderation import moderation
from nuka.moderator import BaseModerator

from .models import Organization


class OrganizationModerator(BaseModerator):
    auto_approve_unless_flagged = False
    visibility_column = 'is_active'


moderation.register(Organization, OrganizationModerator)
