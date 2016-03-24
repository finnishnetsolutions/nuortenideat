# coding=utf-8

from __future__ import unicode_literals

from .models import ClientIdentifier


def get_client_identifier(request):
    ci, _new = ClientIdentifier.objects.get_or_create(
        ip=request.META["REMOTE_ADDR"],
        user_agent=request.META.get("HTTP_USER_AGENT", '-')
    )
    return ci
