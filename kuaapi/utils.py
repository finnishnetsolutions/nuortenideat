# coding=utf-8

from __future__ import unicode_literals

import json
import logging
import re
from operator import itemgetter
from libs.fimunicipality.models import Municipality

from .models import ParticipatingMunicipality


logger = logging.getLogger(__package__)

# Regex to parse municipality code from KUA-supplied url,
# e.g. https://testi.kuntalaisaloite.fi/api/v1/municipalities/92
MUNICIPALITY_CODE_FROM_URL_REGEX = re.compile(r'.*\/([0-9]+)\/?')


def update_participating_municipalities(all_municipalities):
    active_municipalities = filter(itemgetter('active'), all_municipalities)
    active_municipality_codes = set(map(
        lambda m: '%03d' % int(MUNICIPALITY_CODE_FROM_URL_REGEX.match(m['id']).group(1)),
        active_municipalities
    ))

    for participant in ParticipatingMunicipality.objects.exclude(
            municipality__code__in=active_municipality_codes
    ):
        logger.info("Municipality %s no longer participates in KUA, "
                    "deleting participation...", participant.municipality.long_name)
        participant.delete()

    existing_municipality_codes = set(ParticipatingMunicipality.objects\
        .values_list('municipality__code', flat=True))

    new_municipality_codes = active_municipality_codes - existing_municipality_codes

    new_municipality_codes.discard('999')  # "Linda", no such thing...

    new_municipality_count = len(new_municipality_codes)
    if new_municipality_count > 0:
        logger.info("Adding %d new participating municipalities...",
                    new_municipality_count)
        for code in new_municipality_codes:
            logger.info("Adding municipality %s...", code)
            ParticipatingMunicipality.objects.create(
                municipality=Municipality.objects.get(code=code)
            )
    else:
        logger.info("No new municipalities participating in KUA.")

    logger.info("Participating municipalities refreshed.")
