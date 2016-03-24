# coding=utf-8

from __future__ import unicode_literals

import bleach

from django.conf import settings
from django.core.mail.message import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.translation import override, ugettext


def strip_tags(html):
    return bleach.clean((html or '').replace('>', '> '),
                        tags=[], strip=True, strip_comments=True).strip()


def send_email(title=None, msg_template=None, msg_ctx=None, receivers=None, lang='fi',
               attachments=None):
    with override(lang):
        message = render_to_string(msg_template, msg_ctx)
        if hasattr(settings, 'EMAIL_FROM'):
            from_email = settings.EMAIL_FROM
        else:
            from_email = '"%s" <%s@%s>' % (
                ugettext("Nuortenideat.fi"),
                'info',
                settings.EMAIL_FROM_DOMAIN
            )
        headers = {}
        reply_to = getattr(settings, 'EMAIL_REPLY_TO', None)
        if reply_to is not None:
            headers['Reply-To'] = settings.EMAIL_REPLY_TO

        mail = EmailMultiAlternatives(
            subject=title, body=message,
            from_email=from_email, to=receivers,
            headers=headers, attachments=attachments
        )
        mail.send()

        # print("Receiver: {}".format(receivers[0]))
        # print(message)


def send_email_to_multiple_receivers(title=None, msg_template=None, msg_ctx=None,
                                     users=None):
    for u in users:
        send_email(title, msg_template, msg_ctx, [u.settings.email], u.settings.language)


def render_email_template(template, ctx):
    msg = render_to_string(template, ctx)
    msg_lines = msg.strip().splitlines()
    subject = msg_lines[0]
    body = '\n'.join(msg_lines[1:])
    return subject, body.lstrip()


def chunks(l, n):
    for i in xrange(0, len(l), n):
        yield l[i:i+n]
