# coding=utf-8

from __future__ import unicode_literals

from copy import copy
from itertools import chain
import logging
import os
import six
import subprocess

from django.conf import settings

from wkhtmltopdf.utils import _options_to_args
from wkhtmltopdf.views import PDFTemplateResponse

logger = logging.getLogger(__name__)


class WkhtmlToPdfError(Exception):
    pass


def wkhtmltopdf(pages, output=None, **kwargs):
    if isinstance(pages, six.string_types):
        # Support a single page.
        pages = [pages]

    if output is None:
        # Standard output.
        output = '-'

    # Default options:
    options = getattr(settings, 'WKHTMLTOPDF_CMD_OPTIONS', None)
    if options is None:
        options = {'quiet': True}
    else:
        options = copy(options)
    options.update(kwargs)

    # Force --encoding utf8 unless the user has explicitly overridden this.
    options.setdefault('encoding', 'utf8')

    env = getattr(settings, 'WKHTMLTOPDF_ENV', None)
    if env is not None:
        env = dict(os.environ, **env)

    cmd = 'WKHTMLTOPDF_CMD'
    cmd = getattr(settings, cmd, os.environ.get(cmd, 'wkhtmltopdf'))

    ck_args = list(chain(cmd.split(),
                         _options_to_args(**options),
                         list(pages),
                         [output]))
    logger.info(' '.join(ck_args))
    child = subprocess.Popen(ck_args, env=env, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
    output, err = child.communicate()
    if child.poll() != 0:
        if not output[-4:-1] == r'EOF':
            raise WkhtmlToPdfError(err)
        else:
            logger.warn("wkhtmltodpdf: %s", err)
    return output


class BetterPDFTemplateResponse(PDFTemplateResponse):
    def convert_to_pdf(self, filename,
                       header_filename=None, footer_filename=None):
        cmd_options = self.cmd_options.copy()
        # Clobber header_html and footer_html only if filenames are
        # provided. These keys may be in self.cmd_options as hardcoded
        # static files.
        if header_filename is not None:
            cmd_options['header_html'] = header_filename
        if footer_filename is not None:
            cmd_options['footer_html'] = footer_filename
        return wkhtmltopdf(pages=[filename], **cmd_options)
