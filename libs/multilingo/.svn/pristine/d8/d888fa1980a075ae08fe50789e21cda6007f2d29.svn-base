# coding=utf-8

from __future__ import unicode_literals
from json.decoder import JSONDecoder
from json.encoder import JSONEncoder

import six

from django.forms.widgets import TextInput, Textarea
from django.db.models.fields.subclassing import SubfieldBase
from django.utils.encoding import force_unicode
from django.utils.translation import get_language
from django.utils.six import with_metaclass

from json_field.fields import JSONField
from libs.multilingo.forms.fields import MultiLingualField
from libs.multilingo.forms.widgets import MultiLingualWidget

from..utils import MultiLangDict
from ..settings import CONF


class MultilingualTextField(with_metaclass(SubfieldBase, JSONField)):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('help_text', None)
        kwargs.setdefault('default', None if kwargs.get('null') else '')
        kwargs.setdefault('encoder', JSONEncoder)
        kwargs.setdefault('decoder', JSONDecoder)
        self.simultaneous_edit = kwargs.pop('simultaneous_edit', False)
        super(MultilingualTextField, self).__init__(*args, **kwargs)

    def value_from_object(self, obj):
        value = super(JSONField, self).value_from_object(obj)
        return value

    def formfield(self, **kwargs):
        if self.simultaneous_edit:
            kwargs.setdefault('form_class', MultiLingualField)
            kwargs.setdefault('widget', MultiLingualWidget)
        else:
            if self.max_length is None or self.max_length > 255:
                kwargs.setdefault('widget', Textarea)
            else:
                kwargs.setdefault('widget', TextInput)
        return super(JSONField, self).formfield(**kwargs)

    def save_form_data(self, instance, data):
        current_data = getattr(instance, self.name) or {}

        if isinstance(current_data, six.string_types):
            current_data = {CONF['default_language']: current_data}
        elif not isinstance(current_data, dict):
            current_data = {CONF['default_language']: force_unicode(current_data)}

        if isinstance(data, dict):
            current_data = data
        else:
            new_data = {get_language(): data}
            current_data.update(new_data)

        if CONF['remove_empty_translations']:
            for k in current_data.keys():
                if not current_data[k]:
                    del current_data[k]

        setattr(instance, self.name, current_data)

    def to_python(self, value):
        if isinstance(value, MultiLangDict):
            return value
        value = super(MultilingualTextField, self).to_python(value)
        if isinstance(value, six.string_types):
            value = {CONF['default_language']: value}
        if isinstance(value, dict):
            value = MultiLangDict(**value)
        return value

    def get_db_prep_value(self, value, *args, **kwargs):
        if isinstance(value, six.string_types):
            value = {get_language(): value}
        elif not isinstance(value, dict):
            value = {get_language(): force_unicode(value)}
        return super(MultilingualTextField, self).get_db_prep_value(value, *args,
                                                                    **kwargs)
