# coding=utf-8

from __future__ import unicode_literals

from functools import wraps

import six

from django import forms
from django.forms.forms import BoundField
from django.forms.models import ModelFormMetaclass

from .fields import BaseFormidableInlineField, InlineFormSetFieldMixIn


class BoundInlineFormSetField(BoundField):
    @property
    def empty_form(self):
        return self.field.widget.empty_form(self.name + '-{}')

    @property
    def delete_input(self):
        return self.field.widget.delete_input(self.name + '-{}',
                                              getattr(self.value(), 'deleted_pks', []))


class DirtyInlineFormMixIn(object):
    def __init__(self, data=None, **kwargs):
        super(DirtyInlineFormMixIn, self).__init__(data=data, **kwargs)
        if data is not None:
            for field in self.fields.values():
                if isinstance(field, BaseFormidableInlineField):
                    field.widget.dirty = True


class InlineFormSetFieldBindingMixin(object):
    def __getitem__(self, name):
        if isinstance(self.fields.get(name, None), InlineFormSetFieldMixIn):
            return BoundInlineFormSetField(self, self.fields[name], name)
        return super(InlineFormSetFieldBindingMixin, self).__getitem__(name)


class FormidableFormMixIn(DirtyInlineFormMixIn, InlineFormSetFieldBindingMixin):
    pass


class FormidableForm(DirtyInlineFormMixIn, forms.Form):
    pass


class InlineFormSetModelFormMetaclass(ModelFormMetaclass):
    def __new__(mcs, name, bases, attrs):
        new_class = super(InlineFormSetModelFormMetaclass, mcs).__new__(
            mcs, name, bases, attrs
        )
        return new_class


def _run_before(after_func):
    def _inner(before_func):
        @wraps(before_func)
        def runner(*args, **kwargs):
            value = before_func(*args, **kwargs)
            after_func()
            return value
        return runner
    return _inner


class InlineFieldModelFormMixIn(object):
    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        if instance is not None:
            for name, field in self.base_fields.iteritems():
                if isinstance(field, BaseFormidableInlineField):
                    if name not in kwargs.get('initial', {}):
                        kwargs.setdefault('initial', {})
                        kwargs['initial'][name] = self._get_field_initial_from_instance(
                            field, name, instance
                        )
        super(InlineFieldModelFormMixIn, self).__init__(*args, **kwargs)
        if instance is not None:
            for name, field in self.fields.iteritems():
                if isinstance(field, BaseFormidableInlineField) \
                        and field.has_model_form():
                    field.queryset = self._get_inline_queryset(field, name, instance)

    def _get_inline_queryset(self, field, name, instance):
        if hasattr(self, 'get_{}_queryset'.format(name)):
            return getattr(self, 'get_{}_queryset'.format(name))(instance)
        else:
            return field.get_children(instance, name)

    def _get_field_initial_from_instance(self, field, name, instance):
        if hasattr(self, 'get_{}_initial'.format(name)):
            initial = getattr(self, 'get_{}_initial'.format(name))(instance)
        elif field.has_model_form():
            initial = field.get_initial_from_queryset(
                self._get_inline_queryset(field, name, instance)
            )
        else:
            initial = None
        return initial

    def save(self, commit=True):
        instance = super(InlineFieldModelFormMixIn, self).save(commit=commit)

        def save_inline_forms():
            for name, field in self.fields.iteritems():
                if isinstance(field, BaseFormidableInlineField) and \
                                name in self.cleaned_data and field.has_model_form():
                    queryset = self._get_inline_queryset(field, name, instance)
                    assigner = getattr(self, 'assign_{}_parent'.format(name), None)
                    field.save_cleaned_data(instance, queryset, self.cleaned_data[name],
                                            assigner)
        if commit is True:
            save_inline_forms()
        else:
            # HACK: For compatibility, we act like we're m2m.
            self.save_m2m = _run_before(save_inline_forms)(self.save_m2m)

        return instance


class FormidableModelFormMixIn(six.with_metaclass(InlineFormSetModelFormMetaclass,
                                                  FormidableFormMixIn,
                                                  InlineFieldModelFormMixIn)):
    pass


class FormidableModelForm(FormidableModelFormMixIn, forms.BaseModelForm):
    pass
