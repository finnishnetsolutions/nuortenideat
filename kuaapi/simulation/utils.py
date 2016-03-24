# coding=utf-8

from __future__ import unicode_literals

import hashlib


def management_key(initiative_id):
    return hashlib.sha256('p1p12D(cnShdfHDldo12%d' % initiative_id).hexdigest()[:20]
