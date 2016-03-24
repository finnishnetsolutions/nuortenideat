# coding=utf-8

from __future__ import unicode_literals

from django import forms
from django.forms.widgets import HiddenInput
from django.utils.translation import ugettext_lazy as _

from libs.attachtor.utils import get_upload_token

from .widgets import RedactorAttachtorWidget


class UploadSignatureField(forms.CharField):
    widget = HiddenInput

    default_error_messages = {
        'missing_upload_signature': _("Upload signature missing."),
        'invalid_upload_signature': _("Invalid upload signature.")
    }

    def clean(self, value):
        if not value:
            raise forms.ValidationError(
                self.error_messages['missing_upload_signature']
            )
        if value[32:] != get_upload_token(value[:32]):
            raise forms.ValidationError(
                self.error_messages['invalid_upload_signature']
            )
        return value


class RedactorAttachtorFieldMixIn(object):
    widget = RedactorAttachtorWidget

    def __init__(self, *args, **kwargs):
        upload_group_id = kwargs.pop('upload_group_id', None)
        super(RedactorAttachtorFieldMixIn, self).__init__(*args, **kwargs)
        self.upload_group_id = upload_group_id

    def _get_upload_group_id(self):
        return self._upload_group_id

    def _set_upload_group_id(self, val):
        self._upload_group_id = val
        self.widget.upload_group_id = val

    upload_group_id = property(_get_upload_group_id, _set_upload_group_id)


class RedactorAttachtorField(RedactorAttachtorFieldMixIn, forms.CharField):
    pass
