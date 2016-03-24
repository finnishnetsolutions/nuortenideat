# coding=utf-8

from __future__ import unicode_literals

from django import forms
from django.utils.translation import ugettext as _

from . import widgets


class PhoneNumberField(forms.RegexField):
    widget = widgets.PhoneNumberInput
    default_error_message = _("Enter the phone number in an international format "
                              "without dashes or spaces, e.g. +358401234567")

    def __init__(self, **kwargs):
        kwargs.setdefault('error_message', self.default_error_message)
        super(PhoneNumberField, self).__init__('^\+[0-9]{4,20}$', **kwargs)


class BooleanChoiceField(forms.BooleanField):
    label_true = _("Yes")
    label_false = _("No")
    widget = forms.RadioSelect

    def __init__(self, label_true=None, label_false=None, *args, **kwargs):
        kwargs.setdefault('required', False)
        self.choices = kwargs.pop('choices', (
            (True, self.label_true),
            (False, self.label_false),
        ))
        super(BooleanChoiceField, self).__init__(*args, **kwargs)
        self.widget.choices = self.choices
