# coding=utf-8

from __future__ import unicode_literals

from django.core.management import call_command

from celery import shared_task


@shared_task(send_error_emails=False)
def cleanup_chat_users(**kwargs):
    call_command('cleanup_chat_users', **kwargs)
