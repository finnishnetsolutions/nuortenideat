# coding=utf-8

from __future__ import unicode_literals

from django import forms
from django.core.exceptions import ValidationError
from django.forms.models import BaseModelForm
from django.utils.translation import ugettext_lazy as _, ungettext_lazy

from .widgets import InlineFormSetWidgetMixIn, InlineFormSetWidget,\
    InlineFormWidgetMixIn, InlineFormWidget

from .datastructures import CleanedDataWithForm, DataListWithDeletedPKs


class ForcedPrimaryKeyModelFormMixIn(object):
    def __init__(self, *args, **kwargs):
        model_meta = getattr(self.Meta.model, '_meta')
        pk_attr = model_meta.pk.attname
        instance = kwargs.get('instance')
        if instance is not None and instance.pk:
            kwargs.setdefault('initial', {})
            kwargs['initial'][pk_attr] = instance.pk
        super(ForcedPrimaryKeyModelFormMixIn, self).__init__(*args, **kwargs)
        if pk_attr not in self.fields:
            self.add_primary_key_field(pk_attr)

    def add_primary_key_field(self, field_name):
        model_meata = getattr(getattr(self, '_meta').model, '_meta')
        model_pk_field = model_meata.get_field(field_name)
        form_pk_field = model_pk_field.formfield(widget=forms.HiddenInput, required=False)
        if form_pk_field is None:  # Let's assume it's an AutoField
            form_pk_field = forms.IntegerField(widget=forms.HiddenInput, required=False)
        self.fields[field_name] = form_pk_field


class BaseFormidableInlineField(object):
    _queryset = None

    def save_cleaned_data(self, parent_instance, queryset, cleaned_data, assigner):
        raise NotImplementedError

    def get_children(self, instance, field_name):
        raise NotImplementedError

    def assign_parent(self, child_instance, parent_instance):
        setattr(child_instance, self.related_name, parent_instance)

    def get_initial_from_queryset(self, queryset):
        raise NotImplementedError

    def _set_queryset_(self, queryset):
        self.widget.queryset = self._queryset = queryset

    def _get_queryset(self):
        return self._queryset

    def has_model_form(self):
        return issubclass(self.form_class, BaseModelForm)

    queryset = property(_get_queryset, _set_queryset_)


class InlineFormFieldMixIn(BaseFormidableInlineField):
    widget = InlineFormWidget

    default_error_messages = {
        'invalid': _("Unexpected data received."),
        'invalid_child': '',  # Child errors are rendered separately.
        'protected_create': _("Creation of a new related object is disabled."),
        'protected_update': _("Updating of an existing related object is disabled."),
    }

    def __init__(self, form_class, related_name=None, can_update=True, can_create=True,
                 save_unchanged=False, **kwargs):
        widget_class = kwargs.pop('widget', self.widget)
        if not issubclass(widget_class, InlineFormWidgetMixIn):
            raise Exception('widget must be a class inheriting InlineFormWidgetMixIn')
        if issubclass(form_class, forms.BaseModelForm):
            if related_name is None:
                raise Exception('InlineFormFields require related_name kwarg when used '
                                'with a ModelForm.')
        self.related_name = related_name
        self.save_unchanged = save_unchanged
        # These need to be passed to the widget too:
        self.form_class = form_class
        self.can_create = can_create if callable(can_create) else lambda obj: can_create
        self.can_update = can_update if callable(can_update) else lambda obj: can_update
        widget_kwargs = kwargs.pop('widget_kwargs', {})
        widget_kwargs.setdefault('attrs', {})
        widget_kwargs['attrs'].update(kwargs.pop('widget_attrs', {}))
        kwargs['widget'] = widget_class(form_class=form_class, **widget_kwargs)
        super(InlineFormFieldMixIn, self).__init__(**kwargs)

    def clean(self, value):
        form_kwargs = {'data': value}

        if self.queryset is not None:
            instance = self.get_initial_from_queryset(self.queryset)
            form_kwargs['instance'] = instance
        else:
            instance = None

        sub_form = self.form_class(**form_kwargs)

        if value is not None and not isinstance(value, dict):
            raise ValidationError(self.error_message['invalid'])

        if not sub_form.is_valid():
            raise ValidationError(self.error_messages['invalid_child'])

        if instance and instance.pk and sub_form.has_changed() and\
                not self.can_update(instance):
            raise ValidationError(self.error_messages['protected_update'])

        if self.queryset is not None and sub_form.instance.pk is None and\
                not self.can_create(sub_form.instance):
            raise ValidationError(self.error_messages['protected_create'])

        return CleanedDataWithForm(sub_form.cleaned_data, form=sub_form)

    def save_cleaned_data(self, parent_instance, queryset, cleaned_data, assigner=None):
        assigner = assigner or self.assign_parent

        if self.save_unchanged or cleaned_data.cleaned_form.has_changed():
            child_instance = cleaned_data.cleaned_form.save(commit=False)
            assigner(child_instance, parent_instance)
            child_instance.save()
            cleaned_data.cleaned_form.save_m2m()

    def get_children(self, instance, field_name):
        model = getattr(self.form_class, '_meta').model
        return getattr(model, '_default_manager').filter(**{self.related_name: instance})

    def get_initial_from_queryset(self, queryset):
        try:
            return queryset.get()
        except queryset.model.DoesNotExist:
            return None


class InlineFormSetFieldMixIn(BaseFormidableInlineField):
    widget = InlineFormSetWidget

    default_error_messages = {
        'min_forms': ungettext_lazy("At least %(min_forms)s entry is required.",
                                    "At least %(min_forms)s entries are required.",
                                    'min_forms'),
        'max_forms': ungettext_lazy("At most %(max_forms)s entry is allowed.",
                                    "At most %(max_forms)s entries are allowed.",
                                    'max_forms'),
        'invalid': _("Unexpected data received."),
        'invalid_child': '',  # Child errors are rendered separately.
        'invalid_delete_ids': _("Invalid identifiers specified for objects to be "
                                "deleted."),
        'missing_delete_ids': _("Some of the objects specified for deletion do not "
                                "exist."),
        'protected_delete': _("Some of the objects specified for deletion are "
                              "protected."),
        'protected_update': _("Some of the objects changed are protected and can not be "
                              "updated."),
        'update_delete_conflict': _("Can not update and delete the same object."),
        'pk_override': _("Overriding object identifiers is not allowed."),
    }

    def __init__(self, form_class, related_name=None, min_forms=0, max_forms=100,
                 validate_empty=False, initial_forms=0, extra_forms=0, can_update=True,
                 can_delete=True, save_unchanged=False, can_set_pk=False, **kwargs):
        widget_class = kwargs.pop('widget', self.widget)
        if not issubclass(widget_class, InlineFormSetWidgetMixIn):
            raise Exception('widget must be a class inheriting InlineFormSetWidgetMixIn')
        if issubclass(form_class, forms.BaseModelForm):
            if related_name is None:
                raise Exception('InlineFormSetFields require related_name kwarg when '
                                'used with a ModelForm.')
            model_meta = getattr(getattr(form_class, '_meta').model, '_meta')
            if can_update:
                pk_attr = model_meta.pk.attname
                if pk_attr not in form_class.base_fields:
                    form_class = type(str('{}WithPK'.format(form_class.__name__)),
                                      (ForcedPrimaryKeyModelFormMixIn, form_class), {})
        self.related_name = related_name
        self.validate_empty = validate_empty
        self.can_set_pk = can_set_pk
        self.save_unchanged = save_unchanged
        # These need to be passed to the widget too:
        self.form_class = form_class
        self.initial_forms = initial_forms
        self.min_forms = min_forms
        self.max_forms = max_forms
        self.extra_forms = extra_forms
        self.can_delete = can_delete if callable(can_delete) else lambda obj: can_delete
        self.can_update = can_update if callable(can_update) else lambda obj: can_update
        widget_kwargs = kwargs.pop('widget_kwargs', {})
        widget_kwargs.setdefault('attrs', {})
        widget_kwargs['attrs'].update(kwargs.pop('widget_attrs', {}))
        kwargs['widget'] = widget_class(form_class=form_class,
                                        initial_forms=initial_forms,
                                        min_forms=min_forms, max_forms=max_forms,
                                        extra_forms=extra_forms,
                                        can_delete=can_delete,
                                        can_update=can_update,
                                        **widget_kwargs)
        super(InlineFormSetFieldMixIn, self).__init__(**kwargs)

    def _normalize_pk(self, pk_value):
        pk_attr = getattr(self.queryset.model, '_meta').pk.attname
        try:
            return getattr(self.queryset.model, '_meta').get_field(pk_attr)\
                .to_python(pk_value)
        except ValidationError:
            return None

    def _normalized_pk_from_data(self, data):
        if self.queryset is None:
            return None
        pk_attr = getattr(self.queryset.model, '_meta').pk.attname
        if pk_attr not in data:
            return None
        return self._normalize_pk(data[pk_attr])

    def _normalized_pks_from_data(self, data):
        normalized_pks = set()
        for sub_value in data:
            if not isinstance(sub_value, dict):
                raise forms.ValidationError(self.error_messages['invalid'])
            normalized_pk = self._normalized_pk_from_data(sub_value)
            if normalized_pk is not None:
                normalized_pks.add(normalized_pk)
        return normalized_pks

    def clean(self, value):
        failed_validation = 0
        if not hasattr(value, '__iter__'):
            raise forms.ValidationError(self.error_messages['invalid'])
        else:
            if self.queryset is not None:
                existing_pks = self._normalized_pks_from_data(value)
                deleted_pks = filter(None, [self._normalize_pk(pk_value)
                                            for pk_value in value.deleted_pks])
                if len(deleted_pks) < len(value.deleted_pks):
                    raise ValidationError(self.error_messages['invalid_delete_ids'])

                if set(deleted_pks) & set(existing_pks):
                    raise ValidationError(
                        self.error_messages['update_delete_conflict']
                    )

                if deleted_pks:
                    deletable_objs = self.queryset.filter(pk__in=deleted_pks)
                else:
                    deletable_objs = []

                if len(deleted_pks) > len(deletable_objs):
                    raise ValidationError(self.error_messages['missing_delete_ids'])

                for obj in deletable_objs:
                    if not self.can_delete(obj):
                        raise ValidationError(self.error_messages['protected_delete'])

                existing_objs = dict([
                    (obj.pk, obj) for obj in self.queryset.filter(pk__in=existing_pks)
                ])

                if len(existing_objs) < len(existing_pks) and not self.can_set_pk:
                    raise ValidationError(self.error_messages['pk_override'])

            else:
                existing_objs = {}
                deleted_pks = []

            cleaned_data = DataListWithDeletedPKs(deleted_pks=deleted_pks)

            for sub_value in value:
                if sub_value or self.validate_empty:
                    pk_value = self._normalized_pk_from_data(sub_value)
                    if pk_value is not None and pk_value in existing_objs:
                        instance = existing_objs[pk_value]
                        extra = {'instance': instance}
                        allow_update = self.can_update(instance)
                    else:
                        extra = {}
                        allow_update = self.can_update(None)
                    sub_form = self.form_class(data=sub_value, **extra)
                    if not allow_update and sub_form.has_changed():
                        raise forms.ValidationError(
                            self.error_messages['protected_update']
                        )
                    if sub_form.is_valid():
                        cleaned_data.append(CleanedDataWithForm(sub_form.cleaned_data,
                                                                form=sub_form))
                    else:
                        failed_validation += 1

        if failed_validation > 0:
            raise forms.ValidationError(self.error_messages['invalid_child'])
        elif len(cleaned_data) < self.min_forms:
            raise forms.ValidationError(self.error_messages['min_forms'],
                                        params={'min_forms': self.min_forms})
        elif len(cleaned_data) > self.max_forms:
            raise forms.ValidationError(self.error_messages['max_forms'],
                                        params={'max_forms': self.max_forms})
        # TODO: clean unique!
        return cleaned_data

    def save_cleaned_data(self, parent_instance, queryset, cleaned_data, assigner=None):
        assigner = assigner or self.assign_parent

        for cleaned in cleaned_data:
            if self.save_unchanged or cleaned.cleaned_form.has_changed():
                child_instance = cleaned.cleaned_form.save(commit=False)
                assigner(child_instance, parent_instance)
                child_instance.save()
                cleaned.cleaned_form.save_m2m()

        queryset.filter(pk__in=cleaned_data.deleted_pks).delete()

    def get_children(self, instance, field_name):
        return getattr(instance, field_name).all()

    def get_initial_from_queryset(self, queryset):
        return queryset


class InlineFormSetField(InlineFormSetFieldMixIn, forms.Field):
    pass


class InlineFormField(InlineFormFieldMixIn, forms.Field):
    pass
