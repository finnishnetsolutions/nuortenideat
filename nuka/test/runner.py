# coding=utf-8

from __future__ import unicode_literals

from optparse import make_option

from django.conf import settings
from django.test.runner import DiscoverRunner


class CustomPatternTestRunnerMixIn(object):
    @classmethod
    def add_arguments(cls, parser):
        parser.add_argument('-t', '--top-level-directory',
            action='store', dest='top_level', default=None,
            help='Top level of project for unittest discovery.')
        parser.add_argument('-p', '--pattern', action='store', dest='pattern',
            default=settings.DEFAULT_TEST_PATTERN,
            help='The test matching pattern. Defaults to {}.py.'.format(
                settings.DEFAULT_TEST_PATTERN
            ))
        parser.add_argument('-k', '--keepdb', action='store_true', dest='keepdb',
            default=False,
            help='Preserves the test DB between runs.')
        parser.add_argument('-r', '--reverse', action='store_true', dest='reverse',
            default=False,
            help='Reverses test cases order.')
        parser.add_argument('-d', '--debug-sql', action='store_true', dest='debug_sql',
            default=False,
            help='Prints logged SQL queries on failure.')

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('pattern', settings.DEFAULT_TEST_PATTERN)
        super(CustomPatternTestRunnerMixIn, self).__init__(*args, **kwargs)


class TestRunner(CustomPatternTestRunnerMixIn, DiscoverRunner):
    pass

