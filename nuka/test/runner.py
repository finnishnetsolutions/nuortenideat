# coding=utf-8

from __future__ import unicode_literals

from optparse import make_option

from django.conf import settings
from django.test.runner import DiscoverRunner


class CustomPatternTestRunnerMixIn(object):
    option_list = (
        make_option('-t', '--top-level-directory',
            action='store', dest='top_level', default=None,
            help='Top level of project for unittest discovery.'),
        make_option('-p', '--pattern', action='store', dest='pattern',
            default=settings.DEFAULT_TEST_PATTERN,
            help='The test matching pattern. Defaults to %s.' %
                 settings.DEFAULT_TEST_PATTERN),
    )

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('pattern', settings.DEFAULT_TEST_PATTERN)
        super(CustomPatternTestRunnerMixIn, self).__init__(*args, **kwargs)


class TestRunner(CustomPatternTestRunnerMixIn, DiscoverRunner):
    pass

