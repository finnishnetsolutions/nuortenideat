# coding=utf-8

from __future__ import unicode_literals

from rest_framework.permissions import BasePermission, SAFE_METHODS


class ReadOnly(BasePermission):
    """
    Read-only for everyone.
    """
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS
