# coding=utf-8

from __future__ import unicode_literals

from optparse import make_option
import logging

from django.conf import settings
from django.core.management import base

from firebase.firebase import FirebaseAuthentication, FirebaseApplication


logger = logging.getLogger(__name__)


class Command(base.BaseCommand):
    option_list = base.BaseCommand.option_list + (
        make_option('--force', action='store_true', dest='force',
                    default=False, help="Take expired users who don't seem to have any "
                                        "sessions open offline as well."),
    )

    # Delete user info once they've been offline for a week.
    OFFLINE_TIMEOUT = 60 * 60 * 24 * 7
    ONLINE_TIMEOUT = 60

    def handle(self, **options):
        admin_auth = FirebaseAuthentication(settings.FIREBASE['secret'],
                                            'nobody@example.com',
                                            admin=True)
        app = FirebaseApplication(
            settings.FIREBASE['base_url'],
            authentication=admin_auth
        )
        offline_users = []
        deletable_users = []

        cleanup = app.put('cleanup', 'users', {'start': {'.sv': 'timestamp'},
                                               'end': False})
        start = cleanup['start']

        logger.info("User cleanup started (force=%s) %d.", options['force'], start)

        all_users = app.get('/', 'users') or {}

        for uid, user in all_users.iteritems():
            username = user.get('name').lower()
            last_online = user.get('onlineAt', 0)
            sessions = user.get('sessions', [])

            session_age = (start - last_online) // 1000

            if session_age > self.ONLINE_TIMEOUT:
                if sessions:
                    logger.info("%s has been offline for %d seconds but appears online, "
                                "deleting online statuses...",
                                username, session_age)
                    offline_users.append(user)
                elif options['force'] is True:
                    logger.info("%s has been offline for %d seconds and appears offline, "
                                "deleting possible online statuses anyway (because "
                                "force=True)",
                                username, session_age)
                    offline_users.append(user)

            logger.debug('%s has been online for %d seconds', uid, session_age)

            if session_age > self.OFFLINE_TIMEOUT:
                logger.info("%s has been offline for %s seconds, deleting user...",
                            username, session_age)
                deletable_users.append(user)

        if deletable_users or offline_users:
            org_ids_online = (app.get('/', 'organization-admins-online') or {}).keys()
            org_keys = ['organization-admins-online/{}'.format(org_id)
                        for org_id in org_ids_online]

            deletables = set()

            for key in ['user-names-online', 'moderators-online', ] + org_keys:
                usernames = (app.get('/', key) or {}).keys()
                for user in offline_users + deletable_users:
                    deletable_username = user['name'].lower()
                    if deletable_username in usernames:
                        deletables.add((key, deletable_username))
                for user in offline_users:
                    if user.get('sessions'):
                        deletables.add(('users/{}'.format(user['id']), 'sessions'))

            deletables = list(deletables)

            for u in deletable_users:
                deletables.append(('users', u['id']))

            for key, username in deletables:
                logger.info('Deleting %s/%s', key, username)
                app.delete(key, username)

        end = app.put('cleanup/users', 'end', {'.sv': 'timestamp'})

        logger.info("User cleanup ended %d.", end)
