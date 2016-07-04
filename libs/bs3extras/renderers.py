# coding=utf-8

from __future__ import unicode_literals

import logging

from bootstrap3 import renderers
from bootstrap3.forms import render_field

from django.forms.widgets import HiddenInput, TextInput, DateInput, Select
from django.template.context import Context
from django.template.loader import get_template
from django.utils.html import escape


logger = logging.getLogger(__name__)


class BaseFieldRenderer(renderers.FieldRenderer):
    def __init__(self, *args, **kwargs):
        self.button_addon_before = kwargs.get("button_addon_before", "")
        self.button_addon_after = kwargs.get("button_addon_after", "")
        super(BaseFieldRenderer, self).__init__(*args, **kwargs)

    def make_input_group(self, html):
        assert (not (self.button_addon_before and self.addon_before) and
                not (self.button_addon_after and self.addon_after)), \
            "Bootstrap does not support multiple addons on a single side."

        if hasattr(self.widget, "widget_class"):
            widget_class = self.widget.widget_class
        else:
            widget_class = type(self.widget)

        if issubclass(widget_class, (TextInput, DateInput, Select)):
            if self.button_addon_before:
                before = '<span class="input-group-btn">{addon}</span>'.format(
                    addon=self.button_addon_before)
            elif self.addon_before:
                before = '<span class="input-group-addon">{addon}</span>'.format(
                    addon=self.addon_before)
            else:
                before = ''

            if self.button_addon_after:
                after = '<span class="input-group-btn">{addon}</span>'.format(
                    addon=self.button_addon_after)
            elif self.addon_after:
                after = '<span class="input-group-addon">{addon}</span>'.format(
                    addon=self.addon_after)
            else:
                after = ''

            size = self.get_size_class(prefix="input-group")

            if before or after:
                html = '<div class="input-group {size}">{before}{html}{after}</div>' \
                    .format(size=size, before=before, html=html, after=after)

        return html


class WrapIdentifyingFieldRendererMixIn(object):
    def wrap_label_and_field(self, html):
        return '<div id="{field}_wrap" class="{klass}">{content}</div>'.format(
            field=self.field.auto_id,
            klass=self.get_form_group_class(),
            content=html
        )


class WrapIdFieldRenderer(WrapIdentifyingFieldRendererMixIn,
                          BaseFieldRenderer):
    pass


class FieldPreviewRenderer(BaseFieldRenderer):
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

    def add_help_attrs(self, widget=None):
        super(AccessibilityFieldRendererMixIn, self).add_help_attrs(widget=widget)
        if widget is None:
            widget = self.widget
        if self.field_help or self.field_errors:
            widget.attrs['aria-describedby'] = self._help_block_id()
        if self.field_errors:
            widget.attrs['aria-invalid'] = 'true'


class AccessibleWrapIdFieldRenderer(AccessibilityFieldRendererMixIn,
                                    WrapIdFieldRenderer):
    pass


class AccessibleInlineFieldRenderer(AccessibilityFieldRendererMixIn,
                                    renderers.InlineFieldRenderer):
    pass


class InstructionedFieldRendererMixin(object):
    """
    Adds fields instruction_text between label and input.
    Uses CSS class "instruction-block".
    """
    def append_to_field(self, html):
        html = super(InstructionedFieldRendererMixin, self).append_to_field(html)
        form_field = self.field.field
        if hasattr(form_field, "instruction_text") and form_field.instruction_text:
            html = '<span class="instruction-block">{instruction}</span>'.format(
                instruction=form_field.instruction_text
            ) + html
        return html
