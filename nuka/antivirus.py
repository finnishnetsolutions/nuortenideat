# coding=utf-8

"""Based on: https://github.com/budurli/django-antivirus-field"""

from __future__ import unicode_literals

from django.conf import settings

import logging


logger = logging.getLogger(__name__)

ANTIVIRUS_ON = settings.CLAMAV['enabled']


if ANTIVIRUS_ON:
    try:
        import pyclamd

        if settings.CLAMAV['socket'] is None:
            host, port = settings.CLAMAV['address'].split(':')
            logger.info("Connecting to clamd via tcp socket...")
            clam = pyclamd.ClamdNetworkSocket(host=str(host), port=int(port))
        else:
            logger.info("Connecting to clamd via unix socket...")
            clam = pyclamd.ClamdUnixSocket(filename=settings.CLAMAV['socket'])
        clam.ping()
        logger.info("Clamd connection established")

    except Exception as err:
        logger.warn('Problem with ClamAV: {}'.format(str(err)))
        clam = None


def is_infected(stream):
    """
    Create tmp file and scan it with ClamAV
    Returns
        True, 'Virus name' - if virus detected
        False, '' - if not virus detected
        None, '' - status unknown (pyclamd not installed)
    """
    if not ANTIVIRUS_ON or clam is None:
        return None, ''

    result = clam.scan_stream(stream)
    if result:
        result = result['stream']
        if result[0] == 'ERROR':
            logger.warn("ClamAV reported error: %s", result[1])
            return None, result[1]
        elif result[0] == 'FOUND':
            return True, result[1]
        else:
            logger.warn("Unexpected ClamAV scan result: %s", result)
            return None

    return False, ''
