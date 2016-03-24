# conding=utf-8

from __future__ import unicode_literals

from datetime import timedelta, date

from django.conf import settings
from django.core.management.base import BaseCommand

from content.utils import archive_unpublished


class Command(BaseCommand):
    def handle(self, *args, **options):
        archive_date = date.today() - timedelta(days=settings.UNPUBLISHED_ARCHIVING_DAYS)
        archive_unpublished(archive_date)
