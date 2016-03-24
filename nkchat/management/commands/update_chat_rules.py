# coding=utf-8

from __future__ import unicode_literals

from django.conf import settings
from django.core.management.base import NoArgsCommand
from firebase.decorators import http_connection

from firebase.firebase import FirebaseAuthentication, FirebaseApplication, \
    make_put_request


class FirebaseApp(FirebaseApplication):
    @http_connection(60)
    def put_raw(self, url, name, raw_data, connection, params=None, headers=None):
        assert name, 'Snapshot name must be specified'
        params = params or {}
        headers = headers or {}
        endpoint = self._build_endpoint_url(url, name)
        self._authenticate(params, headers)
        return make_put_request(endpoint, raw_data, params, headers,
                                connection=connection)


class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        admin_auth = FirebaseAuthentication(settings.FIREBASE['secret'],
                                            'nobody@example.com',
                                            admin=True, debug=True)
        app = FirebaseApp(
            settings.FIREBASE['base_url'],
            authentication=admin_auth
        )
        rules_data = open(settings.NKCHAT_RULES_PATH, 'rb').read()

        app.put_raw('/.settings', 'rules', rules_data)
