# coding=utf-8

from __future__ import unicode_literals

import logging

from bootstrap3 import renderers
from bootstrap3.forms import render_field, FORM_GROUP_CLASS

from django.forms.widgets import HiddenInput
from django.template.context import Context
from django.template.loader import get_template
from django.utils.html import escape


logger = logging.getLogger(__name__)


class WrapIdentifyingFieldRendererMixIn(object):
    def wrap_label_and_field(self, html):
        klasses = [FORM_GROUP_CLASS,]
        if self.field.field.required:
            klasses.append('required')
        if self.field.errors:
            klasses.append('has-error')
        return '<div id="{field}_wrap" class="{klass}">{content}</div>'.format(
            field=self.field.auto_id,
            klass=' '.join(klasses),
            content=html
        )


class WrapIdFieldRenderer(WrapIdentifyingFieldRendererMixIn,
                          renderers.FieldRenderer):
    pass


class FieldPreviewRenderer(renderers.FieldRenderer):
    def __init__(self, *args, **kwargs):
        logger.debug('render field %s', kwargs)
        self.value_displayer = kwargs.pop('value_displayer', None)
        super(FieldPreviewRenderer, self).__init__(*args, **kwargs)

    def get_label(self):
        return self.field.label

    def render(self):
        html = self.field.as_widget(widget=HiddenInput(),
                                    attrs=self.widget.attrs)
        v = self.value_displayer() if self.value_displayer else self.field.value()
        html += '<p>{0}</p>'.format(escape(v or ''))
        html = html or ''
        html = self.append_to_field(html)
        html = self.add_label(html)
        html = self.wrap_label_and_field(html)
        return html


class WrapIdFieldPreviewRenderer(WrapIdentifyingFieldRendererMixIn,
                                 FieldPreviewRenderer):
    pass


class FormPreviewRenderer(renderers.FormRenderer):
    def render_fields(self):
        rendered_fields = []
        instance = getattr(self.form, 'instance', None)
        for field in self.form:
            rendered_fields.append(render_field(
                field,
                layout=self.layout,
                form_group_class=self.form_group_class,
                field_class=self.field_class,
                label_class=self.label_class,
                show_help=self.show_help,
                exclude=self.exclude,
                set_required=self.set_required,
                value_displayer=getattr(instance, 'get_%s_display' % field.name, field.value) or '' if instance else None
            ))
        return '\n'.join(rendered_fields)


class AccessibilityFieldRendererMixIn(object):
    """
    Adds id-attribute for the field help-block and references it with
    aria-describedby -attribute of the widget. Should make screen readers happier.
    """
    def _help_block_id(self):
        return '%s-help' % self.field.auto_id

    def append_to_field(self, html):
        help_text_and_errors = [self.field_help] + self.field_errors \
            if self.field_help else self.field_errors
        if help_text_and_errors:
            help_html = get_template(
                'bootstrap3/field_help_text_and_errors.html').render(Context({
                'field': self.field,
                'help_text_and_errors': help_text_and_errors,
                'layout': self.layout,
            }))
            html += '<span id="{id}" class="help-block">{help}</span>'.format(
                id=self._help_block_id(),
                help=help_html
            )
        return html

    def add_help_attrs(self):
        super(AccessibilityFieldRendererMixIn, self).add_help_attrs()
        if self.field_help or self.field_errors:
            self.widget.attrs['aria-describedby'] = self._help_block_id()
        if self.field_errors:
            self.widget.attrs['aria-invalid'] = 'true'


class AccessibleWrapIdFieldRenderer(AccessibilityFieldRendererMixIn,
                                    WrapIdFieldRenderer):
    pass


class AccessibleInlineFieldRenderer(AccessibilityFieldRendererMixIn,
                                    renderers.InlineFieldRenderer):
    pass

