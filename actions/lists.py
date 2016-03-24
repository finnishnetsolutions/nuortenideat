# coding=utf-8
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
from content.models import Idea, Question
from actions.models import Action
from nkcomments.models import CustomComment
from nkmessages.models import Message
from nkmoderation.models import ContentFlag
from organization.models import Organization

# possible options
# label
# model
# action_type
# role
# action_subtype
# group
#

NOTIFICATION_OPTIONS = (
    {
        'label': _("Joku kommentoi ideaasi"),
        'model': CustomComment,
        'action_type': Action.TYPE_CREATED,
        'role': Action.ROLE_CONTENT_OWNER,
        'action_subtype': CustomComment.ACTION_SUB_TYPE_IDEA_COMMENTED,
        'group': Action.GROUP_ALL,
    }, {
        'label': _("Kysymykseesi on vastattu / kysymystäsi kommentoidaan"),
        'model': CustomComment,
        'action_type': Action.TYPE_CREATED,
        'role': Action.ROLE_CONTENT_OWNER,
        'action_subtype': CustomComment.ACTION_SUB_TYPE_QUESTION_COMMENTED,
        'group': Action.GROUP_ALL,
    }, {
        'label': _("Oman idean tila muuttuu"),
        'model': Idea,
        'action_type': Action.TYPE_UPDATED,
        'role': Action.ROLE_CONTENT_OWNER,
        'action_subtype': Idea.ACTION_SUB_TYPE_STATUS_UPDATED,
        'group': Action.GROUP_ALL,
    }, {
        'label': _("Organisaatiollesi esitetään idea"),
        'model': Idea,
        'action_type': Action.TYPE_UPDATED,
        'role': Action.ROLE_ORGANIZATION_CONTACT,
        'action_subtype': Idea.ACTION_SUB_TYPE_IDEA_PUBLISHED,
        'group': Action.GROUP_CONTACTS,
    }, {
        'label': _("Organisaatiollesi esitetään kysymys"),
        'model': Question,
        'action_type': Action.TYPE_CREATED,
        'role': Action.ROLE_ORGANIZATION_CONTACT,
        'action_subtype': '',
        'group': Action.GROUP_CONTACTS, },
    {
        'label': _("Organisaatiotasi koskevan idean tila muuttuu"),
        'model': Idea,
        'action_type': Action.TYPE_UPDATED,
        'role': Action.ROLE_ORGANIZATION_CONTACT,
        'action_subtype': Idea.ACTION_SUB_TYPE_STATUS_UPDATED_AFTER_PUBLISH,
        'group': Action.GROUP_CONTACTS,
    }, {
        'label': _("Organisaatiotasi koskevaa ideaa kommentoidaan"),
        'model': CustomComment,
        'action_type': Action.TYPE_CREATED,
        'role': Action.ROLE_ORGANIZATION_CONTACT,
        'action_subtype': CustomComment.ACTION_SUB_TYPE_IDEA_COMMENTED,
        'group': Action.GROUP_CONTACTS,
    }, {
        'label': _("Uusi organisaatio luodaan"),
        'model': Organization,
        'action_type': Action.TYPE_CREATED,
        'role': Action.ROLE_MODERATOR,
        'action_subtype': '',
        'group': Action.GROUP_MODERATORS,
    }, {
        'label': _("Sisältöä ilmoitetaan asiattomaksi"),
        'model': ContentFlag,
        'action_type': Action.TYPE_CREATED,
        'role': Action.ROLE_MODERATOR,
        'action_subtype': '',
        'group': Action.GROUP_MODERATORS,
    },
)