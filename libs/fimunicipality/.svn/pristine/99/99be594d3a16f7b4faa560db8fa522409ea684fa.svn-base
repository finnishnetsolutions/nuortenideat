# coding=utf-8

from __future__ import unicode_literals

from celery import shared_task

from django.core.management import call_command


@shared_task
def sync_municipalities():
    call_command('sync_municipalities')
