# coding=utf-8

from __future__ import unicode_literals

from django import forms
from django.utils.translation import ugettext as _
from django.utils.html import format_html, escape
from django.forms.utils import flatatt
from django.utils.safestring import mark_safe


class PhoneNumberInput(forms.TextInput):
    input_type = 'tel'

    def __init__(self, attrs=None):
        attrs = attrs.copy() if attrs else {}
        if not 'placeholder' in attrs:
            attrs['placeholder'] = _("e.g. +358401234567")
        super(PhoneNumberInput, self).__init__(attrs=attrs)


class ReadOnlyInputMixIn(object):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('attrs', {})
        kwargs['attrs']['readonly'] = 'readonly'
        super(ReadOnlyInputMixIn, self).__init__(*args, **kwargs)


class SelectedLabel(forms.Select):
    def __init__(self, *args, **kwargs):
        self.ignore_attrs = kwargs.pop('ignore_attrs', False)
        super(SelectedLabel, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None, choices=()):
        choices = dict(choices or self.choices)
        if self.ignore_attrs:
            attrs = ''
        else:
            attrs = flatatt(attrs or {})
        if value in choices:
            return mark_safe(format_html('<span{0}>%s</span>', attrs) % escape(choices[value]))
        return ''


class SelectedLabelWithHiddenInput(SelectedLabel, forms.HiddenInput):
    def render(self, name, value, attrs=None, choices=()):
        return super(SelectedLabelWithHiddenInput, self).render(
            name, value, attrs=attrs, choices=choices
        ) + super(forms.HiddenInput, self).render(name, value, attrs=None)


class ReadOnlyTextInput(ReadOnlyInputMixIn, forms.TextInput):
    pass


class ReadOnlyTextarea(ReadOnlyInputMixIn, forms.Textarea):
    pass


class PlainValueSpan(forms.HiddenInput):
    def render(self, name, value, attrs=None):
        hidden_input = super(PlainValueSpan, self)\
            .render(name, value, attrs=attrs)
        return mark_safe(format_html('<span{0}>%s</span>', flatatt(attrs))\
                         % escape(self._format_value(value))) + hidden_input


class NoAutocompleteInputMixIn(object):
    def __init__(self, *args, **kwargs):
        attrs = kwargs.pop('attrs', None) or {}
        attrs['autocomplete'] = "off"
        kwargs['attrs'] = attrs
        super(NoAutocompleteInputMixIn, self).__init__(*args, **kwargs)


class NoAutocompletePasswordInput(NoAutocompleteInputMixIn, forms.PasswordInput):
    pass


class NoAutocompleteTextInput(NoAutocompleteInputMixIn, forms.TextInput):
    pass
