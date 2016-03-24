# coding=utf-8

from __future__ import unicode_literals

from celery.app import shared_task

from django.core.management import call_command


@shared_task
def sync_kua_participants():
    call_command("sync_kua_participants")

