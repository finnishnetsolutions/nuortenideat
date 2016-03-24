# conding=utf-8

from __future__ import unicode_literals

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

import requests

from ...utils import update_participating_municipalities


class Command(BaseCommand):
    @transaction.atomic()
    def handle(self, *args, **options):
        resp = requests.get(settings.KUA_API['participants_url'])
        update_participating_municipalities(resp.json())
