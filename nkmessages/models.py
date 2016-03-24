# coding=utf-8

from __future__ import unicode_literals

from django.db import models
from django.db.models.signals import m2m_changed
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from polymorphic.polymorphic_model import PolymorphicModel
from nuka.utils import send_email


class Message(PolymorphicModel):
    sender = models.ForeignKey("account.User", null=True, on_delete=models.SET_NULL,
                               related_name="sent_messages")
    receivers = models.ManyToManyField("account.User",
                                       related_name="received_messages")
    subject = models.CharField(_("aihe"), max_length=255)
    message = models.CharField(_("viesti"), max_length=4000)
    sent = models.DateTimeField(default=timezone.now)

    read_by = models.ManyToManyField("account.User", related_name="read_messages")
    deleted_by = models.ManyToManyField("account.User",
                                        related_name="deleted_messages")

    # Which message this message is a reply to.
    reply_to = models.ForeignKey("self", null=True, on_delete=models.SET_NULL,
                                 related_name="replies")

    warning = models.BooleanField(_("Varoitusviesti"), default=False)
    to_moderator = models.BooleanField(default=False)
    from_moderator = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("Viesti")
        verbose_name_plural = _("Viestit")


def receivers_added(sender, **kwargs):
    # TODO: siirrä tämä ilmoitustoiminnallisuuteen
    if kwargs['action'] == 'post_add':
        to = kwargs['model'].objects.filter(pk__in=kwargs['pk_set'])
        for user in to:
            if user.settings.message_notification:
                send_email(
                    _("Uusi viesti"),
                    'nkmessages/email/new_message.txt',
                    {'user': user},
                    [user.settings.email],
                    user.settings.language
                )

m2m_changed.connect(receivers_added, sender=Message.receivers.through)


class Feedback(Message):
    name = models.CharField(_("nimi"), blank=True, max_length=50)
    email = models.EmailField(_("sähköposti"), blank=True)

    class Meta:
        verbose_name = _("Palaute")
        verbose_name_plural = _("Palautteet")
