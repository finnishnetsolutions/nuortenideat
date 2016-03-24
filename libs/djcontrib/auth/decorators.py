# coding=utf-8

from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth.decorators import user_passes_test


def superuser_required(func):
    return user_passes_test(lambda u: u.is_active and u.is_superuser,
                            login_url=settings.LOGIN_URL)(func)

def staff_member_required(func):
    """About same as django.contrib.auth.decorators.staff_member_required
    but using settings.LOGIN_URL."""
    return user_passes_test(lambda u: u.is_active and u.is_staff,
                            login_url=settings.LOGIN_URL)(func)
