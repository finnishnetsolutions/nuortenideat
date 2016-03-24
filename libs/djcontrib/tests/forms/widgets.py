# coding=utf-8

from __future__ import unicode_literals

from unittest import TestCase

from django.forms.widgets import TextInput

from ...forms.widgets import ReadOnlyInputMixIn, PlainValueSpan


class ReadOnlyInputTest(TestCase):
    def test_read_only_mixin(self):
        class ReadOnlyTextInput(ReadOnlyInputMixIn, TextInput):
            pass
        self.assertEqual(ReadOnlyTextInput().attrs['readonly'], 'readonly')


class PlainValueSpanTest(TestCase):
    def test_render(self):
        html = PlainValueSpan().render('foo', 'bar', attrs={'do': 'stuff'})
        self.assertEqual(
            html,
            '<span do="stuff">bar</span>'
            '<input do="stuff" name="foo" type="hidden" value="bar" />'
        )
