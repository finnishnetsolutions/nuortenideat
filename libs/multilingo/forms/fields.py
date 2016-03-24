# coding=utf-8

from __future__ import unicode_literals

import copy

from django import forms
from django.utils.translation import ugettext_lazy as _

from libs.multilingo.forms.widgets import MultiLingualWidget, SingleLanguageTextInput

from ..settings import CONF


class SingleLanguageFieldMixIn(object):
    def __init__(self, *args, **kwargs):
        self.language = kwargs.pop('language')
        super(SingleLanguageFieldMixIn, self).__init__(*args, **kwargs)


class SingleLanguageField(SingleLanguageFieldMixIn, forms.CharField):
    pass


class MultiLingualField(forms.MultiValueField):
    widget = MultiLingualWidget

    field_class = SingleLanguageField
    field_widget = SingleLanguageTextInput

    default_error_messages = {
        'invalid': _('Enter translations.'),
        'incomplete': _('Enter all translations.'),
    }

    def __init__(self, *args, **kwargs):
        self.languages = kwargs.pop('languages', CONF['languages'])
        if 'field_class' in kwargs:
            self.field_class = kwargs.pop('field_class')
        kwargs.setdefault('require_all_fields', False)
        kwargs.setdefault('fields', [
            self.field_class(language=lang,
                             max_length=kwargs.pop('max_length', None),
                             required=kwargs['require_all_fields'])
            for lang in self.languages
        ])
        field_widget = kwargs.pop('field_widget', self.field_widget)

        if 'widget' in kwargs:
            if isinstance(kwargs['widget'], type):
                kwargs['widget'] = kwargs['widget'](languages=self.languages,
                                                    widget_class=field_widget)
        else:
            kwargs['widget'] = self.widget(languages=self.languages,
                                           widget_class=self.field_widget)

        super(MultiLingualField, self).__init__(*args, **kwargs)

    def compress(self, data_list):
        comp = dict([(self.languages[i][0], v)
                     for i, v in enumerate(data_list)])
        return comp
