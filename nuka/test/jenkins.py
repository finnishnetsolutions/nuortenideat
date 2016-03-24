# coding=utf-8

from __future__ import unicode_literals

from django.utils.encoding import force_str
from django.utils.unittest import TextTestRunner

from django_jenkins import runner, signals

from .runner import CustomPatternTestRunnerMixIn


class EXMLTestResult(runner.EXMLTestResult):
    def _add_tb_to_test(self, test, test_result, err):
        exc_class, exc_value, tb = err
        tb_str = self._exc_info_to_string(err, test)
        test_result.set('type', '%s.%s' % (exc_class.__module__,
                                           exc_class.__name__))
        test_result.set('message', force_str(exc_value))
        test_result.text = tb_str


class CITestSuiteRunner(CustomPatternTestRunnerMixIn, runner.CITestSuiteRunner):
    def run_suite(self, suite, **kwargs):
        signals.before_suite_run.send(sender=self)
        result = TextTestRunner(buffer=not self.debug,
                                resultclass=EXMLTestResult,
                                verbosity=self.verbosity).run(suite)
        if self.with_reports:
            result.dump_xml(self.output_dir)
        signals.after_suite_run.send(sender=self)
        return result
