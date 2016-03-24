# coding=utf-8

from __future__ import unicode_literals

from django.apps.config import AppConfig


class PermitterAppConfig(AppConfig):
    name = __package__

    def ready(self):
        self.module.autodiscover()
