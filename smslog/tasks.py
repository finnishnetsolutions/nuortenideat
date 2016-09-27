# coding=utf-8
from __future__ import unicode_literals

from datetime import datetime as dt, timedelta
from celery.app import shared_task
from django.conf import settings
from django.core.mail import send_mail

from nuka.utils import render_email_template, send_email
from smslog.models import SentTxtMessages


@shared_task
def send_sms_log_as_email():

    ld = dt.today().replace(day=1) - timedelta(days=1)
    start_date = ld.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    end_date = ld.replace(hour=23, minute=59, second=59, microsecond=0)

    messages = SentTxtMessages.objects.filter(created__range=(start_date, end_date))

    context = {'start_date': start_date, 'end_date': end_date, 'count': messages.count()}

    send_email(
        'Tekstiviestiraportti',
        'smslog/email/sent_txt_messages.txt',
        context,
        [settings.SMS_LOG_EMAIL_RECEIVER, ],
    )
