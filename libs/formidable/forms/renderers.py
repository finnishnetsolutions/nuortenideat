# coding=utf-8

from __future__ import unicode_literals

from bootstrap3 import renderers as bs3
from bootstrap3.forms import render_field

from libs.formidable.forms.fields import InlineFormFieldMixIn, InlineFormSetFieldMixIn
from libs.formidable.forms.widgets import BaseInlineFormidableWidget


class SeamlessInlineFormRendererMixIn(object):
    """Render fields from InlineFormFields as if the fields were part of the parent
    form.

    TODO: How to deal with non-field-errors of the inline form?
    """
    def render_fields(self):
        rendered_fields = []
        for field in self.form:

            if isinstance(field.field, InlineFormFieldMixIn):
                fields = [sub_field for sub_field in field]
            else:
                fields = [field]

            for sub_field in fields:
                rendered_fields.append(render_field(
                    sub_field,
                    layout=self.layout,
                    form_group_class=self.form_group_class,
                    field_class=self.field_class,
                    label_class=self.label_class,
                    show_help=self.show_help,
                    exclude=self.exclude,
                    set_required=self.set_required,
                    size=self.size,
                    horizontal_label_class=self.horizontal_label_class,
                    horizontal_field_class=self.horizontal_field_class,
                ))

        return '\n'.join(rendered_fields)


class SeamlessInlineFormRenderer(SeamlessInlineFormRendererMixIn, bs3.FormRenderer):
    pass


class InlineFormFieldRendererMixIn(object):
    def get_form_group_class(self):
        klasses = super(InlineFormFieldRendererMixIn, self)\
            .get_form_group_class().split(' ')

        if self.field_errors and isinstance(self.field.field, (InlineFormFieldMixIn,
                                                               InlineFormSetFieldMixIn)):
            if not any(self.field_errors):
                klasses = set(klasses) - set(['has-error'])

        return ' '.join(klasses)

    def add_class_attrs(self, widget=None):
        widget = widget or self.widget
        if isinstance(widget, BaseInlineFormidableWidget):
            return
        super(InlineFormFieldRendererMixIn, self).add_class_attrs(widget=widget)


class InlineFormSetFieldRenderer(InlineFormFieldRendererMixIn, bs3.FieldRenderer):
    pass
