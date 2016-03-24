# coding=utf-8
from __future__ import unicode_literals

from datetime import datetime, timedelta
from celery.app import shared_task
from django.utils.translation import ugettext_lazy as _, string_concat

from actions.models import Action, Notification, SentEmails
from nuka.utils import send_email


@shared_task
def create_notifications(action):
    try:
        action.create_notifications()
    except Action.DoesNotExist:
        pass


def collect_and_send_noninstant_notifications(dt, subscription_check_method=None):
    qs = Notification.objects.get_by_date(dt)
    recipients = qs.get_recipients()
    for user in recipients:
        notifications = qs.format_for_user(user, subscription_check_method)
        if notifications:
            # TODO: count_flagged_content_notifications - bad code
            notifications['ContentFlag_moderator_created__count'] = \
                count_flagged_content_notifications(notifications)
            send_notification_emails(user, notifications)


@shared_task
def create_daily_notifications():
    dt = datetime.today() - timedelta(days=1)
    collect_and_send_noninstant_notifications(dt, 'user_has_daily_subscription')


@shared_task
def create_weekly_notifications():
    dt = datetime.today() - timedelta(days=7)
    collect_and_send_noninstant_notifications(dt, 'user_has_weekly_subscription')


def send_notification_emails(user, notifications):
    subject_part_1 = _("Nuortenideat.fi")
    subject_part_2 = _("kooste tapahtumista")
    send_email(string_concat(subject_part_1, ' - ', subject_part_2),
               msg_template='notifications/email/collection.txt',
               msg_ctx={'user': user, 'notifications': notifications},
               receivers=[user.settings.email, ])

    obj = SentEmails(notification=None, email=user.settings.email)
    obj.save()


def count_flagged_content_notifications(notifications):
    key = 'ContentFlag_moderator_created_'
    idea_count = 0
    comment_count = 0
    if key in notifications:
        for n in notifications[key]:
            class_name = n.action.content_object.content_object.__class__.__name__
            if class_name == 'Comment':
                comment_count += 1
            elif class_name == 'Idea':
                idea_count += 1
    return [{'idea_count': idea_count, 'comment_count': comment_count}]