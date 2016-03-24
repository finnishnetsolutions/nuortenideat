# coding=utf-8

from __future__ import unicode_literals

from django.db.models.fields import TextField
from django.utils.encoding import force_text

from ..forms import fields as forms
from ..forms.widgets import RedactorAttachtorWidget
from .. import signals


class RedactorAttachtorFieldMixIn(object):
    widget_class = RedactorAttachtorWidget
    form_class = forms.RedactorAttachtorField

    def __init__(self, *args, **kwargs):
        self.redactor_options = kwargs.pop('redactor_options', {})
        self.allow_file_upload = kwargs.pop('allow_file_upload', True)
        self.allow_image_upload = kwargs.pop('allow_image_upload', True)
        super(RedactorAttachtorFieldMixIn, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        widget = self.widget_class(
            redactor_options=self.redactor_options,
            allow_file_upload=self.allow_file_upload,
            allow_image_upload=self.allow_image_upload
        )
        defaults = {'widget': widget, 'form_class': self.form_class}
        defaults.update(kwargs)
        return super(RedactorAttachtorFieldMixIn, self).formfield(**defaults)

    def contribute_to_class(self, cls, name, virtual_only=False):
        super(RedactorAttachtorFieldMixIn, self).contribute_to_class(cls, name)
        signals.register(cls, name, extractor=self.extract_html_from_field)

    def extract_html_from_field(self, instance, field_name):
        return force_text(getattr(instance, field_name, '') or '')


class RedactorAttachtorField(RedactorAttachtorFieldMixIn, TextField):
    pass
