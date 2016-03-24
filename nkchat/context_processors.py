# coding=utf-8

from __future__ import unicode_literals

from operator import attrgetter, itemgetter
from uuid import uuid4
import datetime

from django.conf import settings
from django.core.cache import caches
from django.utils.functional import SimpleLazyObject
from django.utils.translation import ugettext as _

from firebase_token_generator import create_token

from nuka.perms import IsModerator
from organization.models import Organization


ROLE_ANONYMOUS = 0
ROLE_PARTICIPANT = 1
ROLE_ORGANIZATION_ADMIN = 3
ROLE_MODERATOR = 5

ROLE_PREFIXES = {
    ROLE_ANONYMOUS: 'visitor',
    ROLE_PARTICIPANT: 'participant',
    ROLE_ORGANIZATION_ADMIN: 'organization',
    ROLE_MODERATOR: 'moderator',
}


def _create_auth_token(request, organization_ids):
    roles = []
    user = request.user
    if user.is_authenticated():
        roles.append(ROLE_PARTICIPANT)
        # TODO: is_active=True
        user_id = request.user.username
        name = '@' + user_id
        if IsModerator(request=request).is_authorized():
            roles.append(ROLE_MODERATOR)
        organization_ids = list(organization_ids)
        if len(organization_ids) > 0:
            roles.append(ROLE_ORGANIZATION_ADMIN)
    else:
        roles.append(ROLE_ANONYMOUS)
        if 'firebase' not in request.session:
            if 'redis' in settings.CACHES:
                cache = caches['redis']
                weekly_key = 'firebase_anon_id_%d' % datetime.date.today().isocalendar()[1]
                uid = str(cache.incr(weekly_key))
            else:
                uid = str(uuid4().int)[:6]
            request.session['firebase'] = {
                'id': uid,
                'name': '+anon_' + uid
            }
        user_id = request.session['firebase']['id']
        name = request.session['firebase']['name']
    role = max(roles)
    return create_token(settings.FIREBASE['secret'], {
        'uid': '-'.join([ROLE_PREFIXES[role], user_id]),
        'name': name,
        'role': role,
        'organizations': organization_ids
    })


def _chatty_organizations_ids(user):
    if user.is_authenticated():
        return user.organizations.normal().values_list('pk', flat=True)
    return []


def firebase(request):
    if settings.FIREBASE['enabled']:
        organization_ids = _chatty_organizations_ids(request.user)
        return {
            'firebase': {
                'enabled': True,
                'base_url': settings.FIREBASE['base_url'],
                'auth_token': SimpleLazyObject(
                    lambda: _create_auth_token(request, organization_ids)
                )
            }
        }
    return {}
