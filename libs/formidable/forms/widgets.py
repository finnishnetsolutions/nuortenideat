# coding=utf-8

from __future__ import unicode_literals
import hashlib

from operator import itemgetter
import re
from uuid import uuid4
import simplejson

from django import forms
from django.core.exceptions import ValidationError
from django.db.models.base import Model
from django.forms.utils import flatatt
from django.template.loader import render_to_string
from django.utils.datastructures import MultiValueDict, MergeDict
from django.utils.safestring import mark_safe

from .datastructures import DataListWithDeletedPKs
from ..serializers import LazyJSONEncoder


class InlineFormOptions(object):
    """
    Object attached to inline forms rendered by InlineFormSetWidget as
    form.formidable_opts to provide the form template information needed to control
    object deletion/update.
    """
    def __init__(self, object_id=None, deletable=True, updatable=True):
        self.object_id = object_id or ''
        self.deletable = int(deletable)
        self.updatable = int(updatable)


class BaseInlineFormidableWidget(object):
    def get_form_kwargs_for_data(self, data, prefix, dirty_pks_to_objects):
        form_kwargs = {'prefix': prefix}
        if self.dirty:
            form_kwargs['data'] = dict(('{}-{}'.format(prefix, name), value)
                                       for name, value in data.iteritems())
            pk_attr = self._pk_attr()
            if pk_attr is not None and pk_attr in data:
                instance = dirty_pks_to_objects.get(data[pk_attr])
                if instance is not None:
                    form_kwargs['instance'] = instance
        else:
            if data is None:
                pass
            elif isinstance(data, dict):
                form_kwargs['initial'] = data
            elif issubclass(self.form_class, forms.BaseModelForm) and isinstance(
                    data,
                    getattr(self.form_class, '_meta').model
            ):
                form_kwargs['instance'] = data
            else:
                raise NotImplementedError('unexpected data: {}'.format(data))
        return form_kwargs


class InlineFormWidgetMixIn(BaseInlineFormidableWidget):
    template_name = 'formidable/inline-form-wrap.html'
    form_template_name = 'formidable/inline-form.html'

    def __init__(self, form_class, template_name=None, form_template_name=None,
                 template_context=None, **kwargs):
        self.form_class = form_class
        self.dirty = False
        self.template_name = template_name or self.template_name
        self.template_context = {} if template_context is None \
            else template_context.copy()
        self.template_context['inline_form_template'] = form_template_name \
                                                        or self.form_template_name
        super(InlineFormWidgetMixIn, self).__init__(**kwargs)

    def _pk_attr(self):
        return None  # TODO

    def subwidgets(self, name, value, _attrs=None, _choices=()):
        form = self.form_class(**self.get_form_kwargs_for_data(value, name, {}))
        for field in form:
            yield field

    def render(self, name, value, attrs=None):
        form_id = 'id_formidable_inline_form_{}'.format(uuid4().hex[:10])
        attrs = {} if attrs is None else attrs.copy()
        attrs['class'] = ' '.join([attrs.get('class', ''), 'formidable-inline-form', ])
        final_attrs = self.build_attrs(attrs)
        dirty_pks_to_objects = {}
        form = self.form_class(**self.get_form_kwargs_for_data(value, name,
                                                               dirty_pks_to_objects))
        ctx = self.template_context.copy()
        ctx.update({'form': form,
                    'form_id': form_id,
                    'attrs': flatatt(final_attrs)})
        html = render_to_string(self.template_name, ctx)
        return mark_safe(html)

    def value_from_datadict(self, data, files, name):
        sub_data = {}
        sub_field_regex = re.compile(
            r'^{}\-(?P<sub_field_name>.+)$'.format(
                re.escape(name)
            )
        )
        for key, value in data.iteritems():
            match = sub_field_regex.match(key)
            if match is not None:
                sub_data[match.group('sub_field_name')] = value

        return sub_data


class InlineFormSetWidgetMixIn(BaseInlineFormidableWidget):
    option_serializer = LazyJSONEncoder
    formset_template_name = 'formidable/formset.html'
    form_template_name = 'formidable/formset-form.html'
    queryset = None
    form_wrap_attrs = {'class': 'formidable-form-wrap', }

    def __init__(self, form_class, initial_forms=0, min_forms=0, max_forms=100,
                 extra_forms=0, can_update=True, can_delete=True, form_template_name=None,
                 formset_template_name=None, template_context=None, form_context=None,
                 formset_context=None, form_wrap_attrs=None, **kwargs):
        self.form_class = form_class
        self.initial_forms = initial_forms
        self.min_forms = min_forms
        self.max_forms = max_forms
        self.extra_forms = extra_forms
        self.dirty = False
        self.can_delete = can_delete if callable(can_delete) else lambda obj: can_delete
        self.can_update = can_update if callable(can_update) else lambda obj: can_update
        self.form_template_name = form_template_name or self.form_template_name
        self.formset_template_name = formset_template_name or self.formset_template_name
        self.template_context = {} if template_context is None\
            else template_context.copy()
        self.form_context = {} if form_context is None else form_context.copy()
        self.formset_context = formset_context or {}
        if form_wrap_attrs is None:
            self.form_wrap_attrs = self.__class__.form_wrap_attrs.copy()
        else:
            self.form_wrap_attrs = form_wrap_attrs.copy()
        super(InlineFormSetWidgetMixIn, self).__init__(**kwargs)

    def _pk_attr(self):
        if self.queryset is None:
            return None
        return getattr(self.queryset.model, '_meta').pk.attname

    def _dirty_pks_to_objects(self, data):
        if self.queryset is None:
            return {}
        pk_attr = self._pk_attr()
        pk_field = getattr(self.queryset.model, '_meta').get_field(pk_attr)
        normalized_pks_to_dirty_pks = {}
        for data in data:
            if isinstance(data, dict):  # it might be a Model instance too
                dirty_pk = data.get(pk_attr)
                if dirty_pk:
                    try:
                        normalized_pks_to_dirty_pks[pk_field.to_python(dirty_pk)] =\
                            dirty_pk
                    except ValidationError:
                        pass

        if len(normalized_pks_to_dirty_pks) == 0:
            return {}

        existing_objects = self.queryset.filter(pk__in=normalized_pks_to_dirty_pks.keys())

        return dict((normalized_pks_to_dirty_pks[obj.pk], obj)
                    for obj in existing_objects)

    def render_form(self, form, formset_id=None):
        ctx = self.template_context.copy()
        form_wrap_attrs = self.form_wrap_attrs.copy()
        form_wrap_attrs.update(
            self.get_dynamic_form_wrap_attrs(form)
        )
        ctx.update(self.form_context)
        ctx.update({'form': form,
                    'formset_id': formset_id,
                    'form_wrap_attrs': flatatt(form_wrap_attrs)})
        return render_to_string(self.form_template_name, ctx)

    def get_dynamic_form_wrap_attrs(self, form):
        return {
            'data-object-id': form.formidable_opts.object_id,
            'data-updatable': form.formidable_opts.updatable,
            'data-deletable': form.formidable_opts.deletable,
        }

    def _inline_form_options(self, instance=None):
        return InlineFormOptions(object_id=instance.pk if instance else None,
                                 deletable=self.can_delete(instance),
                                 updatable=self.can_update(instance))

    def subwidgets(self, name, value, attrs=None, choices=()):
        prefix = name + '-{}'

        rendered_forms = 0

        if not value or not hasattr(value, '__iter__'):
            for _form_num in range(0, self.initial_forms):
                form = self.form_class(prefix=prefix.format(rendered_forms))
                form.formidable_opts = self._inline_form_options(None)
                yield form
                rendered_forms += 1
        else:
            dirty_pks_to_objects = self._dirty_pks_to_objects(value)
            for form_data in value:
                if not isinstance(form_data, (dict, Model)):
                    raise Exception('Unexpected form data type: %s' % form_data)
                form_kwargs = self.get_form_kwargs_for_data(
                    form_data, prefix.format(rendered_forms),
                    dirty_pks_to_objects
                )
                form = self.form_class(**form_kwargs)
                form.formidable_opts = self._inline_form_options(getattr(form, 'instance',
                                                                         None))
                yield form
                rendered_forms += 1

            for _form_num in range(0, self.extra_forms):
                if rendered_forms + 1 > self.max_forms:
                    break
                form = self.form_class(prefix=prefix.format(rendered_forms))
                form.formidable_opts = self._inline_form_options(None)
                yield form
                rendered_forms += 1

    def render(self, name, value, attrs=None):
        forms_html = ''
        prefix = name + '-{}'
        rendered_forms = 0

        formset_id = 'id_formidable_formset_{}'.format(uuid4().hex[:10])
        attrs = {} if attrs is None else attrs.copy()
        attrs['class'] = ' '.join([attrs.get('class', ''), formset_id,
                                   'formidable-formset', ])
        attrs['id'] = formset_id
        final_attrs = self.build_attrs(attrs)

        formset_forms = []

        for form in self.subwidgets(name, value, attrs=attrs):
            formset_forms.append(form)
            forms_html += self.render_form(form, formset_id=formset_id)
            rendered_forms += 1

        js_options = {
            'minForms': self.min_forms,
            'maxForms': self.max_forms,
            'nextFormIndex': rendered_forms,
            'deleteInputName': prefix.format('DELETE'),
            'formIndexPlaceHolder': self.form_index_placeholder(prefix)
        }

        js_options.update(final_attrs.pop('formidable', {}))

        if 'newFormTemplate' not in js_options \
                and 'newFormTemplateSelector' not in js_options:
            js_options['newFormTemplate'] = self.render_form(self.empty_form(prefix),
                                                             formset_id=formset_id)

        html = self.render_formset(
            formset_id=formset_id,
            attrs=flatatt(final_attrs),
            forms_html=mark_safe(forms_html),
            delete_input=self.delete_input(prefix,
                                           value=getattr(value, 'deleted_pks', [])),
            forms=formset_forms,
            options_json=mark_safe(simplejson.dumps(js_options,
                                                    cls=self.option_serializer))
        )
        return mark_safe(html)

    def form_index_placeholder(self, prefix=None):
        return '__form_{}_index__'.format(
            hashlib.sha256('dundun' + prefix or '').hexdigest()[:16]
        )

    def empty_form(self, prefix=None):
        form = self.form_class(prefix=prefix.format(self.form_index_placeholder(prefix)))
        form.formidable_opts = InlineFormOptions(deletable=True, updatable=True)
        return form

    def delete_input(self, prefix=None, value=None):
        return forms.SelectMultiple().render(prefix.format('DELETE'), value,
                                             attrs={'style': 'display: none'},
                                             choices=[(v, v) for v in value])

    def render_formset(self, **kwargs):
        ctx = self.template_context.copy()
        ctx.update(self.formset_context.copy())
        ctx.update(kwargs)
        return render_to_string(self.formset_template_name, ctx)

    def value_from_datadict(self, data, files, name):
        sub_data = {}
        sub_field_regex = re.compile(
            r'^{}\-(?P<sub_form_index>[0-9]+)\-(?P<sub_field_name>.+)$'.format(
                re.escape(name)
            )
        )
        for key, value in data.iteritems():
            match = sub_field_regex.match(key)
            if match is not None:
                form_index = int(match.group('sub_form_index'))
                sub_data.setdefault(form_index, {})
                sub_data[form_index][match.group('sub_field_name')] = value
        sub_data = [sdata for _index, sdata in sorted(sub_data.iteritems(),
                                                      key=itemgetter(0))]

        if not isinstance(data, (MultiValueDict, MergeDict)):
            data = MultiValueDict(data.copy())

        deleted_pks = data.getlist('{}-DELETE'.format(name))
        # MultiValueDict.getlist() might return a single element instead of a list...
        if not isinstance(deleted_pks, list):
            deleted_pks = [deleted_pks, ]

        sub_data = DataListWithDeletedPKs(
            sub_data,
            deleted_pks=list(set(deleted_pks))
        )
        return sub_data


class InlineFormSetWidget(InlineFormSetWidgetMixIn, forms.Widget):
    class Media:
        js = ('formidable/js/jquery.formidable.js', )  # pylint: disable=invalid-name


class BootstrapInlineFormSetWidget(InlineFormSetWidget):
    layout = 'default'
    form_template_name = 'formidable/formset-form-bs3.html'

    def __init__(self, *args, **kwargs):
        self.layout = kwargs.pop('layout', self.layout)
        super(BootstrapInlineFormSetWidget, self).__init__(*args, **kwargs)
        self.form_context.setdefault('layout', self.layout)


class InlineFormWidget(InlineFormWidgetMixIn, forms.Widget):
    pass


class BootstrapInlineFormWidget(InlineFormWidget):
    form_template_name = 'formidable/inline-form-bs3.html'
