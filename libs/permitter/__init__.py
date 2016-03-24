# coding=utf-8

from __future__ import unicode_literals

from django.utils.importlib import import_module

from .perms import perms_cache, MinimalPermission


default_app_config = '.'.join([__package__, 'apps',  # pylint: disable=invalid-name
                               'PermitterAppConfig'])


def autodiscover():
    from django.apps import apps
    for app_config in apps.get_app_configs():
        try:
            pkg = import_module('%s.perms' % app_config.name)
            app_perms = dict([
                (name, cls) for name, cls in pkg.__dict__.items()
                if isinstance(cls, type) and issubclass(cls, MinimalPermission)
            ])
            perms_cache[app_config.label] = app_perms
        except ImportError:
            perms_cache[app_config.label] = {}
