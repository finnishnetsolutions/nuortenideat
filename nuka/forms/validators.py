# coding=utf-8

from __future__ import unicode_literals

import logging
import os

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

from ..antivirus import is_infected


logger = logging.getLogger(__package__)


def antivirus_validator(f):
    """Based on: https://github.com/budurli/django-antivirus-field"""

    if not settings.CLAMAV['enabled']:
        logger.warning("ClamAV is not enabled, bypassing virus check for file {}."
                       .format(f.name))
        return

    has_virus, name = is_infected(f.file.read())
    if has_virus:
        raise ValidationError(_("Tiedosto ei läpäissyt virustarkistusta. "
                                "Löytynyt virus: {}").format(name))


def safe_extension_validator(value):
    ext = os.path.splitext(value.name)[1]
    valid_extensions = map(lambda e: '.%s' % e.lower(),
                           settings.FILE_UPLOAD_ALLOWED_EXTENSIONS)
    if ext.lower() not in valid_extensions:
        raise ValidationError(_("Tiedostotyyppi ei ole sallittu."))
