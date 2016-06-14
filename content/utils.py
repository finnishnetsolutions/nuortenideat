# coding=utf-8

from __future__ import unicode_literals

from datetime import date, timedelta

import logging

from django.db.models.query_utils import Q
from django.utils.translation import ugettext as _
from django.utils import timezone

from content.models import Idea
from nkvote.models import Gallup
from nuka.utils import send_email


logger = logging.getLogger(__package__)


def idea_receivers(idea, contact_persons=False):
    if idea.initiator_organization:
        receivers = list(idea.initiator_organization.admins.all())
    else:
        receivers = list(idea.owners.all())

    if contact_persons:
        receivers += [
            admin
            for organization in idea.target_organizations.all()
            for admin in organization.admins.all()
        ]

    return receivers


def warn_unpublished(warn_date, archive_date):
    ideas = Idea.objects.filter(
        Q(status=Idea.STATUS_DRAFT) &
        Q(visibility=Idea.VISIBILITY_PUBLIC) &
        Q(created__lt=warn_date + timedelta(days=1)) &
        Q(created__gte=warn_date)
    )

    unpublished_days = (date.today() - warn_date).days
    archive_days = (warn_date - archive_date).days

    for idea in ideas:
        for receiver in idea_receivers(idea):
            send_email(
                _("Idea '%s' on ollut julkaisematon %d päivää.")
                % (idea.title, unpublished_days),
                "content/email/unpublished_warning.txt",
                {
                    "idea": idea,
                    "unpublished_days": unpublished_days,
                    "archive_days": archive_days,
                },
                [receiver.settings.email],
                receiver.settings.language
            )
            logger.info("Varoitus julkaisemattoman idean %d arkistoinnista lähetetetty "
                        "osoitteeseen %s.", idea.pk, receiver.settings.email)


def archive_unpublished(archive_date):
    ideas = Idea.objects.filter(
        status=Idea.STATUS_DRAFT, created__lt=archive_date + timedelta(days=1)
    ).exclude(
        visibility=Idea.VISIBILITY_ARCHIVED
    )

    for idea in ideas:
        idea.visibility = Idea.VISIBILITY_ARCHIVED
        close_idea_target_gallups(idea)
        idea.save()
        logger.info("Idea %s arkistoitu.", idea.pk)
        for receiver in idea_receivers(idea):
            send_email(
                _("Idea '%s' on arkistoitu.") % idea,
                "content/email/unpublished_archived.txt",
                {
                    "idea": idea,
                    "published_days": (date.today() - archive_date).days,
                },
                [receiver.settings.email],
                receiver.settings.language
            )
            logger.info("Sähköposti idean %d arkistoimisesta lähetetetty "
                        "osoitteeseen %s.", idea.pk, receiver.settings.email)


def remind_untransferred(remind_date, archive_date):
    ideas = Idea.objects.filter(published__startswith=remind_date, status=Idea.STATUS_PUBLISHED,
                                visibility=Idea.VISIBILITY_PUBLIC)

    published_days = (date.today() - remind_date).days
    archive_days = (remind_date - archive_date).days
    for idea in ideas:
        for receiver in idea_receivers(idea, contact_persons=True):
            send_email(
                _("Muistutus idean '%s' viemisestä eteenpäin.") % idea.title,
                "content/email/untransferred_reminder.txt",
                {
                    "idea": idea,
                    "published_days": published_days,
                    "archive_days": archive_days,
                },
                [receiver.settings.email],
                receiver.settings.language
            )
            logger.info("Muistutus idean %d viemisestä eteenpäin lähetetetty "
                        "osoitteeseen %s.", idea.pk, receiver.settings.email)


def warn_untransferred(warn_date, archive_date):
    ideas = Idea.objects.filter(published__startswith=warn_date, status=Idea.STATUS_PUBLISHED,
                                visibility=Idea.VISIBILITY_PUBLIC)

    published_days = (date.today() - warn_date).days
    archive_days = (warn_date - archive_date).days

    for idea in ideas:
        for receiver in idea_receivers(idea, contact_persons=True):
            send_email(
                _("Muistutus idean '%s' viemisestä eteenpäin.") % idea.title,
                "content/email/untransferred_warning.txt",
                {
                    "idea": idea,
                    "published_days": published_days,
                    "archive_days": archive_days,
                },
                [receiver.settings.email],
                receiver.settings.language
            )
            logger.info("Muistutus idean %d viemisestä eteenpäin lähetetetty "
                        "osoitteeseen %s.", idea.pk, receiver.settings.email)


def archive_untransferred(archive_date):
    ideas = Idea.objects.filter(published__lt=archive_date + timedelta(days=1),
                                status=Idea.STATUS_PUBLISHED,
                                visibility=Idea.VISIBILITY_PUBLIC)
    for idea in ideas:
        idea.visibility = Idea.VISIBILITY_ARCHIVED
        idea.save()
        close_idea_target_gallups(idea)
        logger.info("Idea %s arkistoitu.", idea.pk)
        for receiver in idea_receivers(idea, contact_persons=True):
            send_email(
                _("Idea '%s' on arkistoitu.") % idea,
                "content/email/untransferred_archived.txt",
                {
                    "idea": idea,
                    "published_days": (date.today() - archive_date).days,
                },
                [receiver.settings.email],
                receiver.settings.language
            )
            logger.info("Sähköposti idean %d arkistoimisesta lähetetetty "
                        "osoitteeseen %s.", idea.pk, receiver.settings.email)


def close_idea_target_gallups(idea):
    for g in idea.gallup_set.all():
        if g.status == Gallup.STATUS_OPEN:
            g.status = Gallup.STATUS_CLOSED
            g.closed = timezone.now()
            g.save()

    return idea.gallup_set.all()
