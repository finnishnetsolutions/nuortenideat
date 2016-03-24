# coding=utf-8

from __future__ import unicode_literals

from django.conf import settings
from django.http.request import HttpRequest
from django.test import testcases
from django.utils.importlib import import_module


class Client(testcases.Client):
    def login(self, **credentials):
        """
        Copy-pasted from parent, django.contrib.sessions check removed
        """
        from django.contrib.auth import authenticate, login
        user = authenticate(**credentials)
        if (user and user.is_active):
            engine = import_module(settings.SESSION_ENGINE)

            # Create a fake request to store login details.
            request = HttpRequest()

            if self.session:
                request.session = self.session
            else:
                request.session = engine.SessionStore()
            login(request, user)

            # Save the session values.
            request.session.save()

            # Set the cookie to represent the session.
            session_cookie = settings.SESSION_COOKIE_NAME
            self.cookies[session_cookie] = request.session.session_key
            cookie_data = {
                'max-age': None,
                'path': '/',
                'domain': settings.SESSION_COOKIE_DOMAIN,
                'secure': settings.SESSION_COOKIE_SECURE or None,
                'expires': None,
            }
            self.cookies[session_cookie].update(cookie_data)

            return True
        else:
            return False


class TestCase(testcases.TestCase):
    client_class = Client
