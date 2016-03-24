# coding=utf-8

from __future__ import unicode_literals

from django.utils.translation import ugettext as _
from django.conf import settings


def nuka_settings(req):
    site_name = _('Nuortenideat.fi')
    if settings.PRACTICE:
        site_name = _('Nuortenideat.fi harjoittelu')

    return {
        'BASE_URL': settings.BASE_URL,
        'GOOGLE_ANALYTICS_ID': getattr(settings, 'GOOGLE_ANALYTICS_ID', None),
        'PRACTICE': settings.PRACTICE,
        'SITE_NAME': site_name,
        'FB_NK_LOGO_URL': 'nuka/img/nuorten_ideat_logo_fb.png',
        'ABSOLUTE_URI': req.build_absolute_uri(),
    }
